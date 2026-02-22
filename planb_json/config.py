CONFIG = {
  "timezone": "Europe/London",

  "venues": [
    {"slug": "sugden-sports-centre"},
    {"slug": "moss-side-leisure-centre"},
  ],

  "activities": [  # 同时查 40/60
    {"slug": "badminton-60min"},
    {"slug": "badminton-40min"},
  ],

  "booking_release": {  # 放场规则（用于自动计算目标日期）
    "release_hour": 22,
    "release_minute": 0,
    "lead_days": 7,      # 提前一周
    "try_extra_days": 0  # “偷偷放场”探索：>0 就额外扫近几天
  },

  "accounts": [
    {
      "name": "acc1",
      "bearer": "***",              # 本地放，不要提交到 git
      "membership_user_id": 4620321,
      "max_items_per_run": 2,        # 单次最多加车数（保守）
      "allow_same_time_multi_court": False,  # 你担心的限制，先保守
    },
    # 可以继续加 acc2/acc3 ...
  ],

  "request": {
    "target_court_count": 1,         # 只改这个就能订 1/2/3… 片场
    "min_contiguous_minutes": 120,   # 连续时长（例如 120=两小时）
    "prefer_same_court_when_single": True,
  },

  "time_preferences": {
    "weekday_morning": {
      "enabled": True,
      "time_ranges": [("07:00","10:30")],
      "prefer_late": True,
      "prefer_price_pence": 500,     # £5.00 = 500
    },
    "weekday_evening": {
      "enabled": True,
      "time_ranges": [("18:00","22:30")],
      "prefer_late": True,
    },
    "weekend": {
      "enabled": True,
      "prefer_afternoon_first": True,
      "afternoon_range": ("12:00","22:30"),
      "morning_range": ("07:00","12:00"),
      "prefer_late_within_range": True,
    },
  }
}