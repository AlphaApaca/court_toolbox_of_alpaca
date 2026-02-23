# 该代码已废弃，仅保留在这里作为调试时的参考（比如验证 slots 接口的正确性）。正式的预定逻辑请看 bookingstrategy.py。
import json
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import requests

# 调试：指定一个已知可订的时间段（用来验证 slots 链路）
FORCE_TEST_WINDOW = None
# FORCE_TEST_WINDOW = ("2026-02-16", "11:30", "12:30", "458f19d9")

BASE = "https://better-admin.org.uk"
VENUE_SLUG = "sugden-sports-centre"
ACTIVITY_SLUG = "badminton-60min"

# 你的目标：工作日晚18:00以后，越晚越好，连续2小时（两个60min）
TARGET_DATE = "2026-02-23"
AFTER_TIME = "14:30"          # 起始时间阈值（含）
REQUIRE_SAME_COURT = False    # True=两小时必须同一片场；False=两小时可换场

DEBUG_DIR = os.path.join("debug", f"{VENUE_SLUG}_{ACTIVITY_SLUG}", TARGET_DATE)

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


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def save_json(tag: str, payload: Any) -> str:
    ensure_dir(DEBUG_DIR)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    fp = os.path.join(DEBUG_DIR, f"{tag}_{ts}.json")
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return fp


def hm_to_minutes(hm: str) -> int:
    h, m = hm.split(":")
    return int(h) * 60 + int(m)


def minutes_to_hm(minutes: int) -> str:
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"



def find_best_two_hour_pair(
    windows: List[Dict[str, Any]],
    slots_by_start: Dict[str, List[Dict[str, Any]]],
    require_same_court: bool
) -> Optional[Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]]:
    """
    返回: (w1, w2, chosen_slot1, chosen_slot2)
    """
    # 方便查找 t+60
    wmap = {w["start_min"]: w for w in windows}

    candidates = []
    for w1 in windows:
        w2 = wmap.get(w1["start_min"] + 60)
        if not w2:
            continue

        s1 = slots_by_start.get(w1["start"], [])
        s2 = slots_by_start.get(w2["start"], [])
        if not s1 or not s2:
            continue

        if not require_same_court:
            # 任意挑一个即可（你不挑场地）
            chosen1 = s1[0]
            chosen2 = s2[0]
            candidates.append((w1, w2, chosen1, chosen2))
        else:
            # 必须同一片场：用 location.id 交集
            map2 = {slot["location"]["id"]: slot for slot in s2}
            for slot1 in s1:
                cid = slot1["location"]["id"]
                if cid in map2:
                    candidates.append((w1, w2, slot1, map2[cid]))
                    break

    if not candidates:
        return None

    # “越晚越好”：选起始时间最晚的组合
    candidates.sort(key=lambda t: t[0]["start_min"], reverse=True)
    return candidates[0]




# def main():
#     # 以下逻辑是测试已知date，start time, end time, composite key下测试获取指定预定框的所有slots
#     # if FORCE_TEST_WINDOW:
#     #     d, st, et, ck = FORCE_TEST_WINDOW
#     #     print(f"== FORCE TEST slots for {d} {st}-{et} key={ck} ==")
#     #     slots_json = get_slots(d, st, et, ck)
#     #     ok_slots = available_slots_from_slots_response(slots_json)
#     #     print(f"Available courts: {len(ok_slots)}")
#     #     for s in ok_slots[:10]:
#     #         print(f"  court={s['location']['name']}  location_id={s['location']['id']}  slot_id={s['id']}")
#     #     print(f"\nDebug JSON saved under: {DEBUG_DIR}")
#     #     return
    
#     # ensure_dir(DEBUG_DIR)
#     # print(f"== Fetching times for {TARGET_DATE} ==")
    
#     # ==========================================================================
#     # 获取期望日期（TARGET_DATE）的所有可用时间预定（time windows）
#     # 并过滤出起始时间在 AFTER_TIME 之后的（你想要工作日晚18:00后的）可用预定时间窗
#     # ==========================================================================
#     times_json = get_times(TARGET_DATE)
#     windows = build_time_windows(times_json)

#     print(f"Times windows after {AFTER_TIME} (status=BOOK, spaces>0): {len(windows)}")
#     if not windows:
#         print("No available time windows after threshold.")
#         return

#     # ==========================================================================
#     # 逐个 time window 展开 slots
#     # ==========================================================================
#     slots_by_start: Dict[str, List[Dict[str, Any]]] = {}
#     for w in windows:
#         ck = w["composite_key"]
#         if not ck:
#             continue
#         # 轻微节流，避免太密集
#         time.sleep(0.2)
#         slots_json = get_slots(TARGET_DATE, w["start"], w["end"], ck)
#         ok_slots = available_slots_from_slots_response(slots_json)
#         # 按起始时间聚合，方便后续找连续两小时
#         slots_by_start[w["start"]] = ok_slots

#         print(f"- {w['start']}-{w['end']}  key={ck}  time_spaces={w['spaces']}  available_courts={len(ok_slots)}")
#         if ok_slots:
#             # 打印前3个可订场地，方便你看
#             for s in ok_slots[:3]:
#                 loc = s["location"]["name"]
#                 sid = s["id"]
#                 print(f"    court={loc}  slot_id={sid}")

#     # ==========================================================================
#     # 找连续两小时（两个60min）
#     # ==========================================================================
#     best = find_best_two_hour_pair(windows, slots_by_start, REQUIRE_SAME_COURT)
#     if not best:
#         print("\nNo 2-hour consecutive booking found after threshold.")
#         print(f"(require_same_court={REQUIRE_SAME_COURT})")
#         return
    

#     w1, w2, slot1, slot2 = best
#     print("\n== Best 2-hour option (latest start) ==")
#     print(f"Time1: {w1['start']}-{w1['end']}  Court: {slot1['location']['name']}  slot_id={slot1['id']}")
#     print(f"Time2: {w2['start']}-{w2['end']}  Court: {slot2['location']['name']}  slot_id={slot2['id']}")
#     if REQUIRE_SAME_COURT:
#         print("Same-court constraint: satisfied.")
#     else:
#         print("Same-court constraint: not required (may switch courts).")



#     print("\n== Add two-hour booking to cart ==")

#     resp1 = cart_add(
#         slot_id=slot1["id"],
#         pricing_option_id=slot1["pricing_option_id"],
#         membership_user_id=MEMBERSHIP_USER_ID,
#     )

#     resp2 = cart_add(
#         slot_id=slot2["id"],
#         pricing_option_id=slot2["pricing_option_id"],
#         membership_user_id=MEMBERSHIP_USER_ID,
#     )

#     cart1 = resp1.get("data", {})
#     cart2 = resp2.get("data", {})

#     print(f"Cart1 UUID: {cart1.get('uuid')}  items: {cart1.get('item_count')}")
#     print(f"Cart2 UUID: {cart2.get('uuid')}  items: {cart2.get('item_count')}")
#     print(f"Total after second add: {cart2.get('formattedTotal')}")


#     print(f"\nDebug JSON saved under: {DEBUG_DIR}")


# if __name__ == "__main__":
#     main()