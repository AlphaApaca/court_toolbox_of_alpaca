from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from planb_json.config import CONFIG
from planb_json.better_debug import *


def hm_to_min(hm: str) -> int:
    h, m = hm.split(":")
    return int(h) * 60 + int(m)

def min_to_hm(x: int) -> str:
    return f"{x//60:02d}:{x%60:02d}"

@dataclass(frozen=True)
class SlotCandidate:
    venue_slug: str
    activity_slug: str
    date: str
    start: str
    end: str
    start_min: int
    duration_min: int
    slot_id: str
    pricing_option_id: int
    price_pence: int
    location_id: str
    location_name: str

@dataclass
class BookingPlan:
    venue_slug: str
    activity_slug: str
    date: str
    location_id: str
    location_name: str
    slots: List[SlotCandidate]
    total_price_pence: int
    score: float
    reason: str

def build_candidates_from_slots_json(venue_slug: str, activity_slug: str, slots_json: dict) -> List[SlotCandidate]:
    out = []
    for s in slots_json.get("data", []) or []:
        status = (s.get("action_to_show") or {}).get("status")
        spaces = s.get("spaces", 0)
        if status != "BOOK" or not spaces or spaces <= 0:
            continue

        start = s["starts_at"]["format_24_hour"]
        end   = s["ends_at"]["format_24_hour"]
        price_pence = (s.get("price") or {}).get("raw", 0)
        out.append(SlotCandidate(
            venue_slug=venue_slug,
            activity_slug=activity_slug,
            date=s["date"]["raw"] if isinstance(s.get("date"), dict) else s.get("date"),
            start=start,
            end=end,
            start_min=hm_to_min(start),
            duration_min=hm_to_min(end) - hm_to_min(start),
            slot_id=s["id"],
            pricing_option_id=s["pricing_option_id"],
            price_pence=price_pence,
            location_id=s["location"]["id"],
            location_name=s["location"]["name"],
        ))
    return out

def find_contiguous_blocks_per_court(
    cands: List[SlotCandidate],
    after_min: int,
) -> Dict[str, List[List[SlotCandidate]]]:
    """
    返回：每个 location_id 对应若干个“连续块”（按时间连续相接的 slots 列表）
    """
    by_court = defaultdict(list)
    for c in cands:
        if c.start_min >= after_min:
            by_court[c.location_id].append(c)

    blocks_by_court = {}
    for cid, items in by_court.items():
        items.sort(key=lambda x: x.start_min)
        blocks = []
        cur = []
        for s in items:
            if not cur:
                cur = [s]
            else:
                prev = cur[-1]
                # 连续判定：上一段 end == 下一段 start
                if prev.start_min + prev.duration_min == s.start_min:
                    cur.append(s)
                else:
                    blocks.append(cur)
                    cur = [s]
        if cur:
            blocks.append(cur)
        blocks_by_court[cid] = blocks
    return blocks_by_court

def score_evening_plan(slots: List[SlotCandidate], prefer_latest_start: bool = True) -> float:
    """
    晚上：越晚开始越好；如果你也想更长优先，可以再加 duration 权重
    """
    start_min = slots[0].start_min
    duration = sum(s.duration_min for s in slots)
    # 让“更晚开始”主导；同样晚开始时，更长略优
    return (start_min / 10.0) + (duration / 1000.0) if prefer_latest_start else (duration / 10.0)

def build_evening_plans_from_candidates(
    cands: List[SlotCandidate],
    min_contig_min: int,
    after_time: str,
    take_all: bool,
    target_court_count: Optional[int],
    prefer_latest_start: bool,
) -> List[BookingPlan]:
    after_min = hm_to_min(after_time)
    blocks_by_court = find_contiguous_blocks_per_court(cands, after_min)

    plans: List[BookingPlan] = []

    for cid, blocks in blocks_by_court.items():
        for block in blocks:
            total_block_min = sum(s.duration_min for s in block)
            if total_block_min < min_contig_min:
                continue

            # ✅ 关键：你说“>=2h 尽量全拿下”
            # 我们为这片场生成一个 plan：
            # - take_all=True：直接拿“整个连续块”（可能 >2h）
            # - take_all=False：只拿刚好 2h（从最晚开始，或最早开始，按你偏好）
            if take_all:
                chosen = block[:]  # 整段都拿
                reason = f"take_all block {min_to_hm(chosen[0].start_min)} for {total_block_min}min"
            else:
                need = min_contig_min
                # 取最晚开始的一段长度=need：从 block 末尾往前截取 need
                chosen = []
                acc = 0
                for s in reversed(block):
                    chosen.append(s)
                    acc += s.duration_min
                    if acc >= need:
                        break
                chosen.reverse()
                reason = f"take_exact {need}min from latest"

            score = score_evening_plan(chosen, prefer_latest_start=prefer_latest_start)
            total_price = sum(s.price_pence for s in chosen)
            plans.append(BookingPlan(
                venue_slug=chosen[0].venue_slug,
                activity_slug=chosen[0].activity_slug,
                date=chosen[0].date,
                location_id=chosen[0].location_id,
                location_name=chosen[0].location_name,
                slots=chosen,
                total_price_pence=total_price,
                score=score,
                reason=reason
            ))

    # 晚上优先：分数高（更晚）排前
    plans.sort(key=lambda p: p.score, reverse=True)

    # 如果 take_all=True 且 target_court_count=None：就返回全部“满足>=2h”的场
    if target_court_count is None:
        return plans if take_all else plans[:1]

    return plans[:target_court_count]

def execute_evening_plans(plans, membership_user_id, dry_run=False):
    if not plans:
        print("No valid evening plans found.")
        return

    print(f"\n== Found {len(plans)} qualifying courts (>=2h) ==")

    for idx, plan in enumerate(plans, 1):
        print(f"\n[{idx}] {plan.venue_slug} | {plan.location_name}")
        print(f"    start: {plan.slots[0].start}  "
              f"end: {plan.slots[-1].end}  "
              f"total_minutes: {sum(s.duration_min for s in plan.slots)}  "
              f"total_price: £{plan.total_price_pence/100:.2f}")

        if dry_run:
            continue

        for s in plan.slots:
            print(f"    -> adding {s.start}-{s.end}")
            resp = cart_add(
                slot_id=s.slot_id,
                pricing_option_id=s.pricing_option_id,
                membership_user_id=membership_user_id,
            )

        final_cart = resp.get("data", {})
        print(f"    cart_uuid={final_cart.get('uuid')}  "
              f"items={final_cart.get('item_count')}  "
              f"total={final_cart.get('formattedTotal')}")
        

def main():

    candidates = []  # 收集所有 venue + 60/40 的 SlotCandidate

    for venue in CONFIG["venues"]:
        for activity in CONFIG["activities"]:
            # 你已有的 times + slots 拉取逻辑

            # ==========================================================================
            # 获取期望日期（TARGET_DATE）的所有可用时间预定（time windows）
            # 并过滤出起始时间在 AFTER_TIME 之后的（你想要工作日晚18:00后的）可用预定时间窗
            # ==========================================================================
            times_json = get_times(TARGET_DATE)
            windows = build_time_windows(times_json)

            print(f"Times windows after {AFTER_TIME} (status=BOOK, spaces>0): {len(windows)}")
            if not windows:
                print("No available time windows after threshold.")
                return

            # ==========================================================================
            # 逐个 time window 展开 slots
            # ==========================================================================
            slots_by_start: Dict[str, List[Dict[str, Any]]] = {}
            for w in windows:
                ck = w["composite_key"]
                if not ck:
                    continue
                # 轻微节流，避免太密集
                time.sleep(0.2)
                slots_json = get_slots(TARGET_DATE, w["start"], w["end"], ck)
                ok_slots = available_slots_from_slots_response(slots_json)
                # 按起始时间聚合，方便后续找连续两小时
                slots_by_start[w["start"]] = ok_slots

                print(f"- {w['start']}-{w['end']}  key={ck}  time_spaces={w['spaces']}  available_courts={len(ok_slots)}")
                if ok_slots:
                    # 打印前3个可订场地，方便你看
                    for s in ok_slots[:3]:
                        loc = s["location"]["name"]
                        sid = s["id"]
                        print(f"    court={loc}  slot_id={sid}")
    
            # 每个 slots_json 调 build_candidates_from_slots_json()
            candidates.extend(build_candidates_from_slots_json(CONFIG.venue, CONFIG.activities, slots_json))  # to be filled with actual params.

    plans = build_evening_plans_from_candidates(
        cands=candidates,
        min_contig_min=120,
        after_time="18:00",
        take_all=True,             # B 模式
        target_court_count=None,   # 不限制数量
        prefer_latest_start=True,
    )

    execute_evening_plans(
        plans,
        membership_user_id=MEMBERSHIP_USER_ID,
        dry_run=False,
    )
    


if __name__ == "__main__":
    main()

