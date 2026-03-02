import json
import os
import time
import requests
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
from config import CONFIG

BASE = "https://better-admin.org.uk"
AFTER_TIME = "7:00"          # 起始时间阈值（含）
TARGET_DATE = (datetime.now().date() + timedelta(days=7)).isoformat()
# TARGET_DATE = "2026-03-06"  # 固定日期，测试用

HEADERS = {
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Origin": "https://bookings.better.org.uk",
    "Referer": "https://bookings.better.org.uk/location/sugden-sports-centre/badminton-60min/2026-02-16/by-time",
    "Authorization": "Bearer v4.local.jLBnX3BI_OglWC6h5BDCUjTvNJIZ6upauBL27AXHDOKG5t5OcY5HkjpPOlEufvBZRGxc9yBh7slMS4EDGrVzxLO2v2yqrC8Gkfyvp4Jivt6YMbqZhSzvUwpQS7Lla1HKr4BqGclym7xortyqJLo1VIUJru91VfLJgzfZKMXZwGRTWqJAgVpf7Jf8Fnwezq_TO6BZzMqhIak7gnZ4hw"
}
MEMBERSHIP_USER_ID = 4620321

TIMEOUT = 60

# =================================================================
# 0. Basic utils and data structures.
# =================================================================

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


# =================================================================
# 1. API interaction and data parsing.
# =================================================================

def get_times(date_str: str, venue_slug: str, activity_slug: str) -> Dict[str, Any]:
    url = f"{BASE}/api/activities/venue/{venue_slug}/activity/{activity_slug}/v2/times"
    params = {"date": date_str}
    r = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)

    try:
        data = r.json()
    except Exception:
        data = {"_raw_text": r.text}

    if r.status_code != 200:
        print(f"[times] HTTP {r.status_code} for {r.url}")
        # 打印一小段响应体（不要太长）
        snippet = (r.text or "")[:500]
        print(f"[times] body snippet: {snippet!r}")
        # 这里先不 raise，让主流程更可控
        return {"data": [], "_error": {"status": r.status_code, "url": r.url, "body_snippet": snippet}}

    return data


def get_slots(date_str: str, start_hm: str, end_hm: str, composite_key: str, venue_slug: str, activity_slug: str) -> Dict[str, Any]:
    url = f"{BASE}/api/activities/venue/{venue_slug}/activity/{activity_slug}/v2/slots"
    params = {
        "date": date_str,
        "start_time": start_hm,
        "end_time": end_hm,
        "composite_key": composite_key,
    }
    r = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
    try:
        data = r.json()
    except Exception:
        data = {"_raw_text": r.text, "_status_code": r.status_code}
    r.raise_for_status()
    return data

def available_slots_from_slots_response(slots_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    slots = slots_json.get("data", []) or []
    ok = []
    for s in slots:
        status = (s.get("action_to_show") or {}).get("status")
        spaces = s.get("spaces", 0)
        if status == "BOOK" and spaces and spaces > 0:
            ok.append(s)
    return ok

def cart_add(
    slot_id: str,
    pricing_option_id: int,
    membership_user_id: int,
    apply_benefit: bool = True,
    selected_user_id=None,
    activity_restriction_ids=None,
) -> Dict[str, Any]:
    if activity_restriction_ids is None:
        activity_restriction_ids = []

    url = f"{BASE}/api/activities/cart/add"
    payload = {
        "items": [{
            "id": slot_id,
            "type": "purchasableOccurrence",
            "pricing_option_id": pricing_option_id,
            "apply_benefit": apply_benefit,
            "activity_restriction_ids": activity_restriction_ids,
        }],
        "membership_user_id": membership_user_id,
        "selected_user_id": selected_user_id,
    }

    r = requests.post(url, json=payload, headers=HEADERS, timeout=TIMEOUT)

    # 保存响应方便 debug
    try:
        data = r.json()
    except Exception:
        data = {"_raw_text": r.text}

    # save_json("cart_add_response", {
    #     "url": r.url,
    #     "status": r.status_code,
    #     "request_payload": payload,
    #     "response_headers": dict(r.headers),
    #     "json": data,
    # })

    # 失败时也打印信息
    if r.status_code != 200:
        print(f"[cart_add] HTTP {r.status_code} for {r.url}")
        print(f"[cart_add] body_snippet: {(r.text or '')[:800]!r}")
        r.raise_for_status()

    return data


# =================================================================
# 2. Data processing.
# =================================================================

def build_time_windows(times_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    windows = []
    for item in times_json.get("data", []) or []:
        start_hm = item["starts_at"]["format_24_hour"]
        end_hm = item["ends_at"]["format_24_hour"]
        status = (item.get("action_to_show") or {}).get("status")

        if status != "BOOK":
            continue

        windows.append({
            "start": start_hm,
            "end": end_hm,
            "start_min": hm_to_min(start_hm),
            "end_min": hm_to_min(end_hm),
            "composite_key": item.get("composite_key"),
            "spaces": item.get("spaces", None),
            "raw": item,
        })

    # 只保留 start 在 AFTER_TIME 之后的窗口，并按 start 升序排序
    after_min = hm_to_min(AFTER_TIME)
    windows = [w for w in windows if w["start_min"] >= after_min]
    windows.sort(key=lambda x: x["start_min"])
    return windows


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

def summarize_times(times_json: Dict[str, Any], label: str):
    data = times_json.get("data", []) or []
    print(f"[{label}] total times returned: {len(data)}")
    if not data:
        # 可能是接口返回空
        err = times_json.get("_error")
        if err:
            print(f"[{label}] error: {err}")
        return

    # 统计 status 分布
    from collections import Counter
    statuses = []
    after_time = 0
    after_time_book = 0
    for t in data:
        status = (t.get("action_to_show") or {}).get("status", "NONE")
        statuses.append(status)
        st = t["starts_at"]["format_24_hour"]
        if hm_to_min(st) >= hm_to_min(AFTER_TIME):
            after_time += 1
            if status == "BOOK":
                after_time_book += 1

    c = Counter(statuses)
    print(f"[{label}] status counts: {dict(c)}")
    print(f"[{label}] times after {AFTER_TIME}: {after_time}, of which BOOK: {after_time_book}")

# =================================================================
# 3. Booking logic: Find contiguous blocks, design score method.
# =================================================================

# 找连续块的这个算法有问题。具体在chat里面。
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
                cur = [s] #初始化currunt
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

# 相当于是用赋值评分的方式处理时间选择的优先级；会有什么问题？需要再考虑。
# 评分函数：晚上越晚开始越好；如果你也想更长优先，可以再加 duration 权重
def score_evening_plan(slots: List[SlotCandidate], prefer_latest_start: bool = True) -> float:
    """
    晚上：越晚开始越好；如果你也想更长优先，可以再加 duration 权重
    """
    start_min = slots[0].start_min
    duration = sum(s.duration_min for s in slots)
    # 让“更晚开始”主导；同样晚开始时，更长略优
    return (start_min / 10.0) + (duration / 1000.0) if prefer_latest_start else (duration / 10.0)

# =================================================================
# 4. Build plans.
# =================================================================

def build_evening_plans_from_candidates(
    cands: List[SlotCandidate],
    min_contig_min: int, # 连续块的最小总时长（分钟），比如 120
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

            # 这两行是评分系统，目前还没太探索出来实际实现原理先放这里，后续再改。
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

    # 如果 take_all=True 且 target_court_count=None：就返回全部“满足>={min_contig_min}”的场
    if target_court_count is None:
        return plans if take_all else plans[:1]

    return plans[:target_court_count]

# =================================================================
# 5. Execute booking.
# =================================================================

def execute_evening_plans(plans, membership_user_id, dry_run=False, min_contig_min=None):
    if not plans:
        print("No valid evening plans found.")
        return

    print(f"\n== Found {len(plans)} qualifying courts (>={min_contig_min}min) ==")

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
        
# =================================================================
# 6. Release-mode: Polling for availability and auto-booking.
# =================================================================

def run_release_mode(
    duration_seconds: int = 30,
    poll_interval: float = 0.8,
    dry_run: bool = False,
):
    deadline = time.time() + duration_seconds
    last_found = 0

    while time.time() < deadline:
        candidates: List[SlotCandidate] = []

        for venue in CONFIG["venues"]:
            venue_slug = venue["slug"]
            for activity in CONFIG["activities"]:
                activity_slug = activity["slug"]

                times_json = get_times(TARGET_DATE, venue_slug, activity_slug)
                windows = build_time_windows(times_json)

                for w in windows:
                    ck = w.get("composite_key")
                    if not ck:
                        continue
                    slots_json = get_slots(TARGET_DATE, w["start"], w["end"], ck, venue_slug, activity_slug)
                    candidates.extend(build_candidates_from_slots_json(venue_slug, activity_slug, slots_json))

        if candidates:
            last_found = len(candidates)

        plans = build_evening_plans_from_candidates(
            cands=candidates,
            min_contig_min=120,
            after_time=AFTER_TIME,
            take_all=True,
            target_court_count=None,
            prefer_latest_start=True,
        )

        if plans:
            print(f"\n✅ Found {len(plans)} qualifying 2h+ courts. Executing...")
            execute_evening_plans(plans, membership_user_id=MEMBERSHIP_USER_ID, dry_run=dry_run)
            return

        print(f"[poll] candidates={last_found}  plans=0  (sleep {poll_interval}s)")
        time.sleep(poll_interval)

    print("⏱ Release-mode ended: no 2h+ plans found in time window.")
# =================================================================
# 7. Main
# =================================================================
    
def main():
    candidates: List[SlotCandidate] = []

    for venue in CONFIG["venues"]:
        venue_slug = venue["slug"]

        for activity in CONFIG["activities"]:
            activity_slug = activity["slug"]

            # 1) times -> windows
            times_json = get_times(TARGET_DATE, venue_slug, activity_slug)
            # summarize_times(times_json, f"{venue_slug}|{activity_slug}")
            windows = build_time_windows(times_json)

            print(f"\n== {venue_slug} | {activity_slug} ==")
            print(f"Time windows after {AFTER_TIME} (status=BOOK): {len(windows)}")
            if not windows:
                print("No available time windows after threshold for this venue/activity.")
                continue

            # 2) windows -> slots -> candidates
            for w in windows:
                ck = w.get("composite_key")
                if not ck:
                    continue

                time.sleep(0.2) # 避免请求过快被封（可以根据实际情况调整），我想删掉说实话
                slots_json = get_slots(
                    TARGET_DATE,
                    w["start"],
                    w["end"],
                    ck,
                    venue_slug,
                    activity_slug
                )

                # 打印一下该窗口可订场数（可留可删）
                ok_slots = available_slots_from_slots_response(slots_json)
                print(f"- {w['start']}-{w['end']} key={ck} available_courts={len(ok_slots)}")

                # ✅ 关键：用原始 slots_json 构建 candidates
                candidates.extend(build_candidates_from_slots_json(
                    venue_slug=venue_slug,
                    activity_slug=activity_slug,
                    slots_json=slots_json
                ))

    print(f"\nTotal candidates collected: {len(candidates)}")

    plans = build_evening_plans_from_candidates(
        cands=candidates,
        min_contig_min=120,
        after_time=AFTER_TIME,
        take_all=True,             # B 模式：整段拿
        target_court_count=None,   # 不限制数量
        prefer_latest_start=True,
    )

    execute_evening_plans(
        plans,
        membership_user_id=MEMBERSHIP_USER_ID,
        dry_run=False,
        min_contig_min=120,
    )

if __name__ == "__main__":
    main()