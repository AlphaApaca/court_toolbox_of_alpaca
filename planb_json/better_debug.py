import json
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import requests

# 调试：指定一个已知可订的时间段（用来验证 slots 链路）
FORCE_TEST_WINDOW = ("2026-02-16", "11:30", "12:30", "458f19d9")
# 例子：("2026-02-09", "13:30", "14:30", "276d8515")

BASE = "https://better-admin.org.uk"
VENUE_SLUG = "sugden-sports-centre"
ACTIVITY_SLUG = "badminton-60min"

# 你的目标：工作日晚18:00以后，越晚越好，连续2小时（两个60min）
TARGET_DATE = "2026-02-16"
AFTER_TIME = "7:00"          # 起始时间阈值（含）
REQUIRE_SAME_COURT = False    # True=两小时必须同一片场；False=两小时可换场

DEBUG_DIR = os.path.join("debug", f"{VENUE_SLUG}_{ACTIVITY_SLUG}", TARGET_DATE)

# 如果接口需要登录态，最常见是 Cookie 或 Authorization
# 你可以从浏览器 Network 里复制 Request Headers 里的 Cookie/Authorization 填进来
# HEADERS = {
#     "Accept": "application/json, text/plain, */*",
#     "User-Agent": "Mozilla/5.0",
#     "Authorization": "Bearer v4.local.jLBnX3BI_OglWC6h5BDCUjTvNJIZ6upauBL27AXHDOKG5t5OcY5HkjpPOlEufvBZRGxc9yBh7slMS4EDGrVzxLO2v2yqrC8Gkfyvp4Jivt6YMbqZhSzvUwpQS7Lla1HKr4BqGclym7xortyqJLo1VIUJru91VfLJgzfZKMXZwGRTWqJAgVpf7Jf8Fnwezq_TO6BZzMqhIak7gnZ4hw",
#     # "Cookie": "....",
#     "Referer": "https://better-admin.org.uk/",
#     # "Referer": "https://bookings.better.org.uk/location/sugden-sports-centre/badminton-60min/2026-02-18/by-time",
#     # https://better-admin.org.uk/api/activities/venue/sugden-sports-centre/activity/badminton-60min/v2/times?date=2026-02-18
# }
HEADERS = {
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Origin": "https://bookings.better.org.uk",
    "Referer": "https://bookings.better.org.uk/location/sugden-sports-centre/badminton-60min/2026-02-16/by-time",
    "Authorization": "Bearer v4.local.jLBnX3BI_OglWC6h5BDCUjTvNJIZ6upauBL27AXHDOKG5t5OcY5HkjpPOlEufvBZRGxc9yBh7slMS4EDGrVzxLO2v2yqrC8Gkfyvp4Jivt6YMbqZhSzvUwpQS7Lla1HKr4BqGclym7xortyqJLo1VIUJru91VfLJgzfZKMXZwGRTWqJAgVpf7Jf8Fnwezq_TO6BZzMqhIak7gnZ4hw"
}


TIMEOUT = 20


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

def get_times(date_str: str) -> Dict[str, Any]:
    url = f"{BASE}/api/activities/venue/{VENUE_SLUG}/activity/{ACTIVITY_SLUG}/v2/times"
    params = {"date": date_str}
    r = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)

    # 无论成功失败都先保存，便于排查
    try:
        data = r.json()
    except Exception:
        data = {"_raw_text": r.text}

    save_json("times_response", {"url": r.url, "status": r.status_code, "headers": dict(r.headers), "json": data})

    if r.status_code != 200:
        print(f"[times] HTTP {r.status_code} for {r.url}")
        # 打印一小段响应体（不要太长）
        snippet = (r.text or "")[:500]
        print(f"[times] body snippet: {snippet!r}")
        # 这里先不 raise，让主流程更可控
        return {"data": [], "_error": {"status": r.status_code, "url": r.url, "body_snippet": snippet}}

    return data



def get_slots(date_str: str, start_hm: str, end_hm: str, composite_key: str) -> Dict[str, Any]:
    url = f"{BASE}/api/activities/venue/{VENUE_SLUG}/activity/{ACTIVITY_SLUG}/v2/slots"
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
    save_json(f"slots_{start_hm}_{end_hm}", {"url": r.url, "status": r.status_code, "json": data})
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


def build_time_windows(times_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    windows = []
    for item in times_json.get("data", []) or []:
        start_hm = item["starts_at"]["format_24_hour"]
        end_hm = item["ends_at"]["format_24_hour"]
        status = (item.get("action_to_show") or {}).get("status")
        spaces = item.get("spaces", 0)
        if status == "BOOK" and spaces and spaces > 0:
            windows.append({
                "start": start_hm,
                "end": end_hm,
                "start_min": hm_to_minutes(start_hm),
                "end_min": hm_to_minutes(end_hm),
                "composite_key": item.get("composite_key"),
                "spaces": spaces,
                "raw": item,
            })
    # 只保留 18:00 之后
    after_min = hm_to_minutes(AFTER_TIME)
    windows = [w for w in windows if w["start_min"] >= after_min]
    # 按时间排序
    windows.sort(key=lambda x: x["start_min"])
    return windows


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


def main():
    if FORCE_TEST_WINDOW:
        d, st, et, ck = FORCE_TEST_WINDOW
        print(f"== FORCE TEST slots for {d} {st}-{et} key={ck} ==")
        slots_json = get_slots(d, st, et, ck)
        ok_slots = available_slots_from_slots_response(slots_json)
        print(f"Available courts: {len(ok_slots)}")
        for s in ok_slots[:10]:
            print(f"  court={s['location']['name']}  location_id={s['location']['id']}  slot_id={s['id']}")
        print(f"\nDebug JSON saved under: {DEBUG_DIR}")
        return
    
    ensure_dir(DEBUG_DIR)
    print(f"== Fetching times for {TARGET_DATE} ==")
    
    times_json = get_times(TARGET_DATE)
    windows = build_time_windows(times_json)

    print(f"Times windows after {AFTER_TIME} (status=BOOK, spaces>0): {len(windows)}")
    if not windows:
        print("No available time windows after threshold.")
        return

    # 逐个 time window 展开 slots
    slots_by_start: Dict[str, List[Dict[str, Any]]] = {}
    for w in windows:
        ck = w["composite_key"]
        if not ck:
            continue
        # 轻微节流，避免太密集
        time.sleep(0.2)
        slots_json = get_slots(TARGET_DATE, w["start"], w["end"], ck)
        ok_slots = available_slots_from_slots_response(slots_json)
        slots_by_start[w["start"]] = ok_slots

        print(f"- {w['start']}-{w['end']}  key={ck}  time_spaces={w['spaces']}  available_courts={len(ok_slots)}")
        if ok_slots:
            # 打印前3个可订场地，方便你看
            for s in ok_slots[:3]:
                loc = s["location"]["name"]
                sid = s["id"]
                print(f"    court={loc}  slot_id={sid}")

    # 找连续两小时（两个60min）
    best = find_best_two_hour_pair(windows, slots_by_start, REQUIRE_SAME_COURT)
    if not best:
        print("\nNo 2-hour consecutive booking found after threshold.")
        print(f"(require_same_court={REQUIRE_SAME_COURT})")
        return

    w1, w2, slot1, slot2 = best
    print("\n== Best 2-hour option (latest start) ==")
    print(f"Time1: {w1['start']}-{w1['end']}  Court: {slot1['location']['name']}  slot_id={slot1['id']}")
    print(f"Time2: {w2['start']}-{w2['end']}  Court: {slot2['location']['name']}  slot_id={slot2['id']}")
    if REQUIRE_SAME_COURT:
        print("Same-court constraint: satisfied.")
    else:
        print("Same-court constraint: not required (may switch courts).")

    print(f"\nDebug JSON saved under: {DEBUG_DIR}")


if __name__ == "__main__":
    main()