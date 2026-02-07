# 将关键选择器集中管理，便于后续维护与回放
# Centralized management of key selectors for easier maintenance and replay

LOGIN_EMAIL = "input[type='email']"
LOGIN_PASSWORD = "input[type='password']"
LOGIN_SUBMIT = "button[type='submit'], button[type='button'][data-qa='login-submit']"

# 场馆搜索/选择
VENUE_SEARCH_INPUT = "input[type='search'], input[placeholder*='location']"
VENUE_RESULT_ITEM = "a"  # 需根据实际 DOM 调整

# 日期/时间槽
DATE_PICKER = "button[data-qa='date-picker'], input[type='date']"
TIME_SLOT = "button[data-qa='timeslot'], button[data-qa='book-slot'], .timeslot"

# 加入购物车
ADD_TO_BASKET = "button[data-qa='add-to-basket'], button[data-qa='add-to-cart']"
VIEW_BASKET = "a[href*='basket'], button[data-qa='view-basket']"
