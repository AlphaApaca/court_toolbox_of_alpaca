# 基本信息

登陆URL: https://bookings.better.org.uk/location/sugden-sports-centre
https://bookings.better.org.uk/location/moss-side-leisure-centre

book URL: https://bookings.better.org.uk/location/sugden-sports-centre/badminton-60min/2026-01-13/by-time

Booking flow: 
    I have both app and web. Which one is easier?
    existing account:
        email address: mingyang.xu-3@postgrad.manchester.ac.uk
        password: Alpaca@betteruk_4436

Constraints: 
    location: Sugden sports centre
    how far: A week in advance at ten o 'clock at night. This means that all the venue reservations for next Thursday will be available at 10 p.m. this Thursday.
    payment: You just need to add it to the shopping cart, and the final payment operation will be completed manually.

Environment:
    selenium
    没有任何限制

Robustness:
    It seems that this website doesn't handle verification codes. Do you have any other suggestions?

## 目前阶段的如下问题：

### 1. 官方放出时间不确定

目前比较合适的场馆有两个：sugden-sports-centre和moss-side-leisure-centre
每个场馆中，有多个羽毛球场地，但是不知道每天场官方会放出哪些时间段的羽毛球场地。
但是我可以简单梳理一下我期望的预定逻辑。

我刚发现了一个很诡异的事情，我在明天和后天都有别人拉我球局，但是网站上并没有显示出预定的时间段，而是返回空，说明空不一定是官方没有放出场地，也有可能是所有场地都已经被预定（但是为什么这个时候不显示full？还是说，显示full的时候并不是完全不可以预定，而是有人加入购物车之后还没有付款，所以显示full）anyway，我只要一直发送请求，读"times?date=xxxx"response里面的data信息就可以。

### 2. 预定逻辑实现

如果工作日（周一到周五）能有晚上的场地，最好预定晚上的（18点以后，包含18点开始的）。
如果是周六周天，那么上午9点以后开始的场地都可以预定，如果可用的时段很多，优先选连续的两个小时内场地最多的时段。
这其实给我一个启发，我能不能专门写一个函数来设计预定逻辑，来保证当我想改变我自己期望的时间段和场地时只需要改变这一个函数中的参数就可以？
如果要做到这一点，我应该在运行这个函数前就把所有可用预定（所有时间段的所有场地信息）全部获取到，

### 3. 两个预定时间不定放出

并且，每个场馆（sugden和moss side）的可选预定时间都有两个badminton-60min和badminton-40min。对于badminton-60min，一般要订到至少连续的2h（两个预定），最多4h（四个预定）（如果后面有机会延续富贵杯）。对于badminton-40min，一般要订到连续的2h（三个预定）最多4h（六个预定）。最好有几个账号并行预定。



关于订场策略，我们能不能写一个函数来掌握？

因为：

1. 不是所有的时候我都想订晚上的场地，
2. 有的时候我甚至还需要同时用不同的账号一起预定（同一账号有最大预定数量，我还没有测试，而且同一账号同一时间段可能不能预定多片场地，我也没有测试，后续我们可以把这些的相关逻辑测试一下），
3. 有的时候我还要抢周六周天的场地，那又是不同的策略。
4. 我希望能在每天晚上十点钟准时自动启动预定程序。因为场馆方释放场地一般来说是在提前一周的晚上十点释放，也就是说，如果今天是周二，那么下周二的所有可预定的场地将会在今天晚上十点准时释放。（我们也在探索场馆方有没有偷偷放场地的可能，比如在今天周二突然偷偷放出一堆在下周二之前的日期的可用预定，但是最早的释放场地的策略应该提前一周）
5. 我希望能够只修改参数来调整我期望预定的场地数量，

关于订场逻辑策略：

1. 我希望我只通过更改参数实现不同的预定策略，因为可能会很复杂
2. 我希望通过更改期望时间（或时间区间），来预定不同时间段的预定（XX时间）
   + 时间预定逻辑基本需要包括以下逻辑：1. 只选择连续的XX时间的预定。2. 如果预定在工作日的早上，早上有5镑一个小时的场地，请尽可能选择5镑的可用预定中更晚的时间段（一般最晚是9:30-10:30的预定）3. 如果预定在工作日晚上，请尽可能选择从最晚可用预定开始往前的可用的XX时间的预定。4. 如果预定在周六和周天，尽量选择下午的预定（12点以后），如果没有再选择上午的预定。5. better uk的羽毛球预定每个场馆都有两种可选的时间段长度：badminton-40min和badminton-60min，我希望能够自动同时查找这两种可选时间段长度的所有预定（他们是不同的）
3. 我希望通过更改预定场地数量，来操作多个账号实现同时预定同一时段的不同场地，同时，如果只预定一个场地，优先选择几个时间段内同一场地的预定。
4. 我希望同时抢sugden-sports-centre和moss-side-leisure-centre（或更多场馆）的预定。有的时候我可能会选择有更多期望可用预定场馆。

### 4. others

另外一个有趣的想法：业余羽毛球等级分制。(画大饼)

## JSON:

Badminton60:

Request URL: https://better-admin.org.uk/api/activities/venue/sugden-sports-centre/categories/badminton-60min

Request Method: GET

Status Code: 200 OK

Remote Address: 52.209.12.194:443

Referrer Policy: no-referrer-when-downgrade

Response JSON: 

```json
{
    "data": {
        "v2": true,
        "id": "01973a79-17dc-7137-bc6c-9c04873a10e4",
        "v2Id": "01973a79-17dc-7137-bc6c-9c04873a10e4",
        "name": "Badminton 60min",
        "slug": "badminton-60min",
        "v2_slug": "badminton-60min",
        "v1_slug": null,
        "v1_type": null,
        "v2_type": "resources",
        "allocation_strategy": "customer",
        "image": "",
        "browse_by_name": "location",
        "has_children": false,
        "parent_slug": "badminton",
        "parent_name": "Badminton",
        "is_root": false,
        "children": [],
        "locations": [
            {
                "id": "5043",
                "name": "Hall A, Crt 1",
                "type": "resource",
                "slug": "hall-a-crt-1",
                "venue_id": 90266,
                "venue_slug": "sugden-sports-centre"
            },
            {
                "id": "5044",
                "name": "Hall A, Crt 2",
                "type": "resource",
                "slug": "hall-a-crt-2",
                "venue_id": 90266,
                "venue_slug": "sugden-sports-centre"
            },
            {
                "id": "5045",
                "name": "Hall A, Crt 3",
                "type": "resource",
                "slug": "hall-a-crt-3",
                "venue_id": 90266,
                "venue_slug": "sugden-sports-centre"
            },
            {
                "id": "5051",
                "name": "Hall C, Crt 1",
                "type": "resource",
                "slug": "hall-c-crt-1",
                "venue_id": 90266,
                "venue_slug": "sugden-sports-centre"
            },
            {
                "id": "5052",
                "name": "Hall C, Crt 2",
                "type": "resource",
                "slug": "hall-c-crt-2",
                "venue_id": 90266,
                "venue_slug": "sugden-sports-centre"
            },
            {
                "id": "5053",
                "name": "Hall C, Crt 3",
                "type": "resource",
                "slug": "hall-c-crt-3",
                "venue_id": 90266,
                "venue_slug": "sugden-sports-centre"
            },
            {
                "id": "5054",
                "name": "Hall C, Crt 4",
                "type": "resource",
                "slug": "hall-c-crt-4",
                "venue_id": 90266,
                "venue_slug": "sugden-sports-centre"
            },
            {
                "id": "5055",
                "name": "Hall D, Crt 5",
                "type": "resource",
                "slug": "hall-d-crt-5",
                "venue_id": 90266,
                "venue_slug": "sugden-sports-centre"
            },
            {
                "id": "5056",
                "name": "Hall D, Crt 6",
                "type": "resource",
                "slug": "hall-d-crt-6",
                "venue_id": 90266,
                "venue_slug": "sugden-sports-centre"
            },
            {
                "id": "5057",
                "name": "Hall D, Crt 7",
                "type": "resource",
                "slug": "hall-d-crt-7",
                "venue_id": 90266,
                "venue_slug": "sugden-sports-centre"
            },
            {
                "id": "5058",
                "name": "Hall D, Crt 8",
                "type": "resource",
                "slug": "hall-d-crt-8",
                "venue_id": 90266,
                "venue_slug": "sugden-sports-centre"
            },
            {
                "id": "5046",
                "name": "Sports Hall A&B Court 4, Sugden Sports Centre",
                "type": "resource",
                "slug": "sports-hall-ab-court-4-sugden-sports-centre",
                "venue_id": 90266,
                "venue_slug": "sugden-sports-centre"
            }
        ]
    }
}
```

Dates:



```json
{
    "data": [
        {
            "raw": "2026-02-09",
            "day_pretty": "Monday",
            "date_pretty": "9 Feb",
            "today": true,
            "full_date_pretty": "Mon 9 Feb",
            "year": "2026"
        },
        {
            "raw": "2026-02-10",
            "day_pretty": "Tuesday",
            "date_pretty": "10 Feb",
            "today": false,
            "full_date_pretty": "Tue 10 Feb",
            "year": "2026"
        },
        {
            "raw": "2026-02-11",
            "day_pretty": "Wednesday",
            "date_pretty": "11 Feb",
            "today": false,
            "full_date_pretty": "Wed 11 Feb",
            "year": "2026"
        },
        {
            "raw": "2026-02-12",
            "day_pretty": "Thursday",
            "date_pretty": "12 Feb",
            "today": false,
            "full_date_pretty": "Thu 12 Feb",
            "year": "2026"
        },
        {
            "raw": "2026-02-13",
            "day_pretty": "Friday",
            "date_pretty": "13 Feb",
            "today": false,
            "full_date_pretty": "Fri 13 Feb",
            "year": "2026"
        },
        {
            "raw": "2026-02-14",
            "day_pretty": "Saturday",
            "date_pretty": "14 Feb",
            "today": false,
            "full_date_pretty": "Sat 14 Feb",
            "year": "2026"
        },
        {
            "raw": "2026-02-15",
            "day_pretty": "Sunday",
            "date_pretty": "15 Feb",
            "today": false,
            "full_date_pretty": "Sun 15 Feb",
            "year": "2026"
        }
    ]
}
```

##### times?date=2026-02-09:

Request URL: https://better-admin.org.uk/api/activities/venue/sugden-sports-centre/activity/badminton-60min/v2/times?date=2026-02-09

Request Method: GET

Status Code: 200 OK

Remote Address: 52.209.12.194:443

Referrer Policy: no-referrer-when-downgrade

Response JSON: 

```json
{
    "data": [
        {
            "starts_at": {
                "format_12_hour": "01:30pm",
                "format_24_hour": "13:30"
            },
            "ends_at": {
                "format_12_hour": "02:30pm",
                "format_24_hour": "14:30"
            },
            "duration": "60min",
            "price": {
                "is_estimated": true,
                "formatted_amount": "\u00a39.00"
            },
            "composite_key": "276d8515",
            "timestamp": 1770643800,
            "booking": null,
            "action_to_show": {
                "status": "BOOK",
                "reason": null
            },
            "category_slug": "badminton-60min",
            "date": "2026-02-09",
            "venue_slug": "sugden-sports-centre",
            "location": "Multiple",
            "spaces": 1,
            "name": "Badminton 60min",
            "allows_anonymous_bookings": false,
            "restrictions": {
                "pre_waiver": null,
                "pre_induction": null,
                "criteria": null
            },
            "has_pre_purchase_restrictions": false,
            "requires_induction": false,
            "restriction_ids": []
        },
        {
            "starts_at": {
                "format_12_hour": "02:00pm",
                "format_24_hour": "14:00"
            },
            "ends_at": {
                "format_12_hour": "03:00pm",
                "format_24_hour": "15:00"
            },
            "duration": "60min",
            "price": {
                "is_estimated": true,
                "formatted_amount": "\u00a39.00"
            },
            "composite_key": "8e7d6b51",
            "timestamp": 1770645600,
            "booking": null,
            "action_to_show": {
                "status": "BOOK",
                "reason": null
            },
            "category_slug": "badminton-60min",
            "date": "2026-02-09",
            "venue_slug": "sugden-sports-centre",
            "location": "Multiple",
            "spaces": 1,
            "name": "Badminton 60min",
            "allows_anonymous_bookings": false,
            "restrictions": {
                "pre_waiver": null,
                "pre_induction": null,
                "criteria": null
            },
            "has_pre_purchase_restrictions": false,
            "requires_induction": false,
            "restriction_ids": []
        },
        {
            "starts_at": {
                "format_12_hour": "02:30pm",
                "format_24_hour": "14:30"
            },
            "ends_at": {
                "format_12_hour": "03:30pm",
                "format_24_hour": "15:30"
            },
            "duration": "60min",
            "price": {
                "is_estimated": true,
                "formatted_amount": "\u00a39.00"
            },
            "composite_key": "dd6b8c2e",
            "timestamp": 1770647400,
            "booking": null,
            "action_to_show": {
                "status": "BOOK",
                "reason": null
            },
            "category_slug": "badminton-60min",
            "date": "2026-02-09",
            "venue_slug": "sugden-sports-centre",
            "location": "Multiple",
            "spaces": 2,
            "name": "Badminton 60min",
            "allows_anonymous_bookings": false,
            "restrictions": {
                "pre_waiver": null,
                "pre_induction": null,
                "criteria": null
            },
            "has_pre_purchase_restrictions": false,
            "requires_induction": false,
            "restriction_ids": []
        },
        {
            "starts_at": {
                "format_12_hour": "03:00pm",
                "format_24_hour": "15:00"
            },
            "ends_at": {
                "format_12_hour": "04:00pm",
                "format_24_hour": "16:00"
            },
            "duration": "60min",
            "price": {
                "is_estimated": true,
                "formatted_amount": "\u00a39.00"
            },
            "composite_key": "bb4f5c04",
            "timestamp": 1770649200,
            "booking": null,
            "action_to_show": {
                "status": "FULL",
                "reason": "The session being booked is already full"
            },
            "category_slug": "badminton-60min",
            "date": "2026-02-09",
            "venue_slug": "sugden-sports-centre",
            "location": "Multiple",
            "spaces": 0,
            "name": "Badminton 60min",
            "allows_anonymous_bookings": false,
            "restrictions": {
                "pre_waiver": null,
                "pre_induction": null,
                "criteria": null
            },
            "has_pre_purchase_restrictions": false,
            "requires_induction": false,
            "restriction_ids": []
        },
        {
            "starts_at": {
                "format_12_hour": "03:30pm",
                "format_24_hour": "15:30"
            },
            "ends_at": {
                "format_12_hour": "04:30pm",
                "format_24_hour": "16:30"
            },
            "duration": "60min",
            "price": {
                "is_estimated": true,
                "formatted_amount": "\u00a39.00"
            },
            "composite_key": "c60730c7",
            "timestamp": 1770651000,
            "booking": null,
            "action_to_show": {
                "status": "BOOK",
                "reason": null
            },
            "category_slug": "badminton-60min",
            "date": "2026-02-09",
            "venue_slug": "sugden-sports-centre",
            "location": "Multiple",
            "spaces": 1,
            "name": "Badminton 60min",
            "allows_anonymous_bookings": false,
            "restrictions": {
                "pre_waiver": null,
                "pre_induction": null,
                "criteria": null
            },
            "has_pre_purchase_restrictions": false,
            "requires_induction": false,
            "restriction_ids": []
        }
    ]
}
```

##### slots?date=2026-02-09&start_time=13:30&end_time=14:30&composite_key=276d8515:

Request URL: https://better-admin.org.uk/api/activities/venue/sugden-sports-centre/activity/badminton-60min/v2/slots?date=2026-02-09&start_time=13:30&end_time=14:30&composite_key=276d8515

Request Method: GET

Status Code: 200 OK

Remote Address: 52.209.12.194:443

Referrer Policy: no-referrer-when-downgrade

Response JSON: 

```json
{
    "data": [
        {
            "id": "AQGbDtNYefSCkMux0b1JMy8D9-C9kfdu6A",
            "name": "Badminton 60min",
            "allows_anonymous_bookings": false,
            "pre_booking_notice": null,
            "root_activity_category": {
                "v2": true,
                "id": "01973a77-cc91-71b2-9a81-2dd265c72a35",
                "v2Id": "01973a77-cc91-71b2-9a81-2dd265c72a35",
                "name": "Badminton",
                "slug": "badminton",
                "v2_slug": "badminton",
                "v1_slug": null,
                "path": "badminton",
                "v1_type": null,
                "v2_type": null,
                "allocation_strategy": "customer",
                "image": "",
                "parent_slug": null,
                "has_children": false,
                "is_root": true
            },
            "category_slug": "badminton-60min",
            "duration": "60min",
            "instructors": [],
            "date": {
                "raw": "2026-02-09",
                "raw_pretty": "09\/02\/2026",
                "day_pretty": "Mon",
                "date_pretty": "9 Feb",
                "full_date_pretty": "Mon 09 February 2026",
                "full_date": "09 February 2026",
                "difference": "41 seconds ago",
                "tz": "Europe\/London"
            },
            "location": {
                "id": "5051",
                "name": "Hall C, Crt 1",
                "type": "resource",
                "slug": "hall-c-crt-1",
                "venue_id": 90266,
                "venue_slug": "sugden-sports-centre"
            },
            "slot_display_location": "Hall C, Crt 1",
            "price": {
                "benefit_applied": false,
                "package_applied": false,
                "formatted": "\u00a39.00",
                "raw": 900
            },
            "starts_at": {
                "format_12_hour": "1:30pm",
                "format_24_hour": "13:30"
            },
            "ends_at": {
                "format_12_hour": "2:30pm",
                "format_24_hour": "14:30"
            },
            "last_bookable_at": {
                "format_12_hour": "1:35pm",
                "format_24_hour": "13:35"
            },
            "venue_name": "Sugden Sports Centre",
            "pricing_option_id": 992,
            "cart_type": "purchasableOccurrence",
            "composite_key": "276d8515",
            "booking": null,
            "bookings_count": 1,
            "spaces": 0,
            "capacity": 1,
            "action_to_show": {
                "status": "FULL",
                "reason": "The session being booked is already full"
            },
            "waitlist_id": null,
            "restrictions": {
                "pre_waiver": null,
                "pre_induction": null,
                "criteria": null
            },
            "has_pre_purchase_restrictions": false,
            "requires_induction": false,
            "restriction_ids": [],
            "benefit_available": null,
            "tags": []
        },
        {
            "id": "AQGbDtunTP1InFEHzkrYwLYD9-C9kfdu6A",
            "name": "Badminton 60min",
            "allows_anonymous_bookings": false,
            "pre_booking_notice": null,
            "root_activity_category": {
                "v2": true,
                "id": "01973a77-cc91-71b2-9a81-2dd265c72a35",
                "v2Id": "01973a77-cc91-71b2-9a81-2dd265c72a35",
                "name": "Badminton",
                "slug": "badminton",
                "v2_slug": "badminton",
                "v1_slug": null,
                "path": "badminton",
                "v1_type": null,
                "v2_type": null,
                "allocation_strategy": "customer",
                "image": "",
                "parent_slug": null,
                "has_children": false,
                "is_root": true
            },
            "category_slug": "badminton-60min",
            "duration": "60min",
            "instructors": [],
            "date": {
                "raw": "2026-02-09",
                "raw_pretty": "09\/02\/2026",
                "day_pretty": "Mon",
                "date_pretty": "9 Feb",
                "full_date_pretty": "Mon 09 February 2026",
                "full_date": "09 February 2026",
                "difference": "41 seconds ago",
                "tz": "Europe\/London"
            },
            "location": {
                "id": "5052",
                "name": "Hall C, Crt 2",
                "type": "resource",
                "slug": "hall-c-crt-2",
                "venue_id": 90266,
                "venue_slug": "sugden-sports-centre"
            },
            "slot_display_location": "Hall C, Crt 2",
            "price": {
                "benefit_applied": false,
                "package_applied": false,
                "formatted": "\u00a39.00",
                "raw": 900
            },
            "starts_at": {
                "format_12_hour": "1:30pm",
                "format_24_hour": "13:30"
            },
            "ends_at": {
                "format_12_hour": "2:30pm",
                "format_24_hour": "14:30"
            },
            "last_bookable_at": {
                "format_12_hour": "1:35pm",
                "format_24_hour": "13:35"
            },
            "venue_name": "Sugden Sports Centre",
            "pricing_option_id": 992,
            "cart_type": "purchasableOccurrence",
            "composite_key": "276d8515",
            "booking": null,
            "bookings_count": 1,
            "spaces": 0,
            "capacity": 1,
            "action_to_show": {
                "status": "FULL",
                "reason": "The session being booked is already full"
            },
            "waitlist_id": null,
            "restrictions": {
                "pre_waiver": null,
                "pre_induction": null,
                "criteria": null
            },
            "has_pre_purchase_restrictions": false,
            "requires_induction": false,
            "restriction_ids": [],
            "benefit_available": null,
            "tags": []
        },
        {
            "id": "AQGbDttXpPTvnOXBBcx8-BwD9-C9kfdu6A",
            "name": "Badminton 60min",
            "allows_anonymous_bookings": false,
            "pre_booking_notice": null,
            "root_activity_category": {
                "v2": true,
                "id": "01973a77-cc91-71b2-9a81-2dd265c72a35",
                "v2Id": "01973a77-cc91-71b2-9a81-2dd265c72a35",
                "name": "Badminton",
                "slug": "badminton",
                "v2_slug": "badminton",
                "v1_slug": null,
                "path": "badminton",
                "v1_type": null,
                "v2_type": null,
                "allocation_strategy": "customer",
                "image": "",
                "parent_slug": null,
                "has_children": false,
                "is_root": true
            },
            "category_slug": "badminton-60min",
            "duration": "60min",
            "instructors": [],
            "date": {
                "raw": "2026-02-09",
                "raw_pretty": "09\/02\/2026",
                "day_pretty": "Mon",
                "date_pretty": "9 Feb",
                "full_date_pretty": "Mon 09 February 2026",
                "full_date": "09 February 2026",
                "difference": "41 seconds ago",
                "tz": "Europe\/London"
            },
            "location": {
                "id": "5053",
                "name": "Hall C, Crt 3",
                "type": "resource",
                "slug": "hall-c-crt-3",
                "venue_id": 90266,
                "venue_slug": "sugden-sports-centre"
            },
            "slot_display_location": "Hall C, Crt 3",
            "price": {
                "benefit_applied": false,
                "package_applied": false,
                "formatted": "\u00a39.00",
                "raw": 900
            },
            "starts_at": {
                "format_12_hour": "1:30pm",
                "format_24_hour": "13:30"
            },
            "ends_at": {
                "format_12_hour": "2:30pm",
                "format_24_hour": "14:30"
            },
            "last_bookable_at": {
                "format_12_hour": "1:35pm",
                "format_24_hour": "13:35"
            },
            "venue_name": "Sugden Sports Centre",
            "pricing_option_id": 992,
            "cart_type": "purchasableOccurrence",
            "composite_key": "276d8515",
            "booking": null,
            "bookings_count": 1,
            "spaces": 0,
            "capacity": 1,
            "action_to_show": {
                "status": "FULL",
                "reason": "The session being booked is already full"
            },
            "waitlist_id": null,
            "restrictions": {
                "pre_waiver": null,
                "pre_induction": null,
                "criteria": null
            },
            "has_pre_purchase_restrictions": false,
            "requires_induction": false,
            "restriction_ids": [],
            "benefit_available": null,
            "tags": []
        },
        {
            "id": "AQGbDqXaNvMjnSiTlChdX14D9-C9kfdu6A",
            "name": "Badminton 60min",
            "allows_anonymous_bookings": false,
            "pre_booking_notice": null,
            "root_activity_category": {
                "v2": true,
                "id": "01973a77-cc91-71b2-9a81-2dd265c72a35",
                "v2Id": "01973a77-cc91-71b2-9a81-2dd265c72a35",
                "name": "Badminton",
                "slug": "badminton",
                "v2_slug": "badminton",
                "v1_slug": null,
                "path": "badminton",
                "v1_type": null,
                "v2_type": null,
                "allocation_strategy": "customer",
                "image": "",
                "parent_slug": null,
                "has_children": false,
                "is_root": true
            },
            "category_slug": "badminton-60min",
            "duration": "60min",
            "instructors": [],
            "date": {
                "raw": "2026-02-09",
                "raw_pretty": "09\/02\/2026",
                "day_pretty": "Mon",
                "date_pretty": "9 Feb",
                "full_date_pretty": "Mon 09 February 2026",
                "full_date": "09 February 2026",
                "difference": "41 seconds ago",
                "tz": "Europe\/London"
            },
            "location": {
                "id": "5054",
                "name": "Hall C, Crt 4",
                "type": "resource",
                "slug": "hall-c-crt-4",
                "venue_id": 90266,
                "venue_slug": "sugden-sports-centre"
            },
            "slot_display_location": "Hall C, Crt 4",
            "price": {
                "benefit_applied": false,
                "package_applied": false,
                "formatted": "\u00a39.00",
                "raw": 900
            },
            "starts_at": {
                "format_12_hour": "1:30pm",
                "format_24_hour": "13:30"
            },
            "ends_at": {
                "format_12_hour": "2:30pm",
                "format_24_hour": "14:30"
            },
            "last_bookable_at": {
                "format_12_hour": "1:35pm",
                "format_24_hour": "13:35"
            },
            "venue_name": "Sugden Sports Centre",
            "pricing_option_id": 992,
            "cart_type": "purchasableOccurrence",
            "composite_key": "276d8515",
            "booking": null,
            "bookings_count": 1,
            "spaces": 0,
            "capacity": 1,
            "action_to_show": {
                "status": "FULL",
                "reason": "The session being booked is already full"
            },
            "waitlist_id": null,
            "restrictions": {
                "pre_waiver": null,
                "pre_induction": null,
                "criteria": null
            },
            "has_pre_purchase_restrictions": false,
            "requires_induction": false,
            "restriction_ids": [],
            "benefit_available": null,
            "tags": []
        },
        {
            "id": "AQGbDqfiuv3UkfL3eeWyyxAD9-C9kfdu6A",
            "name": "Badminton 60min",
            "allows_anonymous_bookings": false,
            "pre_booking_notice": null,
            "root_activity_category": {
                "v2": true,
                "id": "01973a77-cc91-71b2-9a81-2dd265c72a35",
                "v2Id": "01973a77-cc91-71b2-9a81-2dd265c72a35",
                "name": "Badminton",
                "slug": "badminton",
                "v2_slug": "badminton",
                "v1_slug": null,
                "path": "badminton",
                "v1_type": null,
                "v2_type": null,
                "allocation_strategy": "customer",
                "image": "",
                "parent_slug": null,
                "has_children": false,
                "is_root": true
            },
            "category_slug": "badminton-60min",
            "duration": "60min",
            "instructors": [],
            "date": {
                "raw": "2026-02-09",
                "raw_pretty": "09\/02\/2026",
                "day_pretty": "Mon",
                "date_pretty": "9 Feb",
                "full_date_pretty": "Mon 09 February 2026",
                "full_date": "09 February 2026",
                "difference": "41 seconds ago",
                "tz": "Europe\/London"
            },
            "location": {
                "id": "5055",
                "name": "Hall D, Crt 5",
                "type": "resource",
                "slug": "hall-d-crt-5",
                "venue_id": 90266,
                "venue_slug": "sugden-sports-centre"
            },
            "slot_display_location": "Hall D, Crt 5",
            "price": {
                "benefit_applied": false,
                "package_applied": false,
                "formatted": "\u00a39.00",
                "raw": 900
            },
            "starts_at": {
                "format_12_hour": "1:30pm",
                "format_24_hour": "13:30"
            },
            "ends_at": {
                "format_12_hour": "2:30pm",
                "format_24_hour": "14:30"
            },
            "last_bookable_at": {
                "format_12_hour": "1:35pm",
                "format_24_hour": "13:35"
            },
            "venue_name": "Sugden Sports Centre",
            "pricing_option_id": 992,
            "cart_type": "purchasableOccurrence",
            "composite_key": "276d8515",
            "booking": null,
            "bookings_count": 1,
            "spaces": 0,
            "capacity": 1,
            "action_to_show": {
                "status": "FULL",
                "reason": "The session being booked is already full"
            },
            "waitlist_id": null,
            "restrictions": {
                "pre_waiver": null,
                "pre_induction": null,
                "criteria": null
            },
            "has_pre_purchase_restrictions": false,
            "requires_induction": false,
            "restriction_ids": [],
            "benefit_available": null,
            "tags": []
        },
        {
            "id": "AQGbDqYSXfpzujsimIQMno0D9-C9kfdu6A",
            "name": "Badminton 60min",
            "allows_anonymous_bookings": false,
            "pre_booking_notice": null,
            "root_activity_category": {
                "v2": true,
                "id": "01973a77-cc91-71b2-9a81-2dd265c72a35",
                "v2Id": "01973a77-cc91-71b2-9a81-2dd265c72a35",
                "name": "Badminton",
                "slug": "badminton",
                "v2_slug": "badminton",
                "v1_slug": null,
                "path": "badminton",
                "v1_type": null,
                "v2_type": null,
                "allocation_strategy": "customer",
                "image": "",
                "parent_slug": null,
                "has_children": false,
                "is_root": true
            },
            "category_slug": "badminton-60min",
            "duration": "60min",
            "instructors": [],
            "date": {
                "raw": "2026-02-09",
                "raw_pretty": "09\/02\/2026",
                "day_pretty": "Mon",
                "date_pretty": "9 Feb",
                "full_date_pretty": "Mon 09 February 2026",
                "full_date": "09 February 2026",
                "difference": "41 seconds ago",
                "tz": "Europe\/London"
            },
            "location": {
                "id": "5056",
                "name": "Hall D, Crt 6",
                "type": "resource",
                "slug": "hall-d-crt-6",
                "venue_id": 90266,
                "venue_slug": "sugden-sports-centre"
            },
            "slot_display_location": "Hall D, Crt 6",
            "price": {
                "benefit_applied": false,
                "package_applied": false,
                "formatted": "\u00a39.00",
                "raw": 900
            },
            "starts_at": {
                "format_12_hour": "1:30pm",
                "format_24_hour": "13:30"
            },
            "ends_at": {
                "format_12_hour": "2:30pm",
                "format_24_hour": "14:30"
            },
            "last_bookable_at": {
                "format_12_hour": "1:35pm",
                "format_24_hour": "13:35"
            },
            "venue_name": "Sugden Sports Centre",
            "pricing_option_id": 992,
            "cart_type": "purchasableOccurrence",
            "composite_key": "276d8515",
            "booking": null,
            "bookings_count": 1,
            "spaces": 0,
            "capacity": 1,
            "action_to_show": {
                "status": "FULL",
                "reason": "The session being booked is already full"
            },
            "waitlist_id": null,
            "restrictions": {
                "pre_waiver": null,
                "pre_induction": null,
                "criteria": null
            },
            "has_pre_purchase_restrictions": false,
            "requires_induction": false,
            "restriction_ids": [],
            "benefit_available": null,
            "tags": []
        },
        {
            "id": "AQGbDqZ1K_m5khhfmCsT0SID9-C9kfdu6A",
            "name": "Badminton 60min",
            "allows_anonymous_bookings": false,
            "pre_booking_notice": null,
            "root_activity_category": {
                "v2": true,
                "id": "01973a77-cc91-71b2-9a81-2dd265c72a35",
                "v2Id": "01973a77-cc91-71b2-9a81-2dd265c72a35",
                "name": "Badminton",
                "slug": "badminton",
                "v2_slug": "badminton",
                "v1_slug": null,
                "path": "badminton",
                "v1_type": null,
                "v2_type": null,
                "allocation_strategy": "customer",
                "image": "",
                "parent_slug": null,
                "has_children": false,
                "is_root": true
            },
            "category_slug": "badminton-60min",
            "duration": "60min",
            "instructors": [],
            "date": {
                "raw": "2026-02-09",
                "raw_pretty": "09\/02\/2026",
                "day_pretty": "Mon",
                "date_pretty": "9 Feb",
                "full_date_pretty": "Mon 09 February 2026",
                "full_date": "09 February 2026",
                "difference": "41 seconds ago",
                "tz": "Europe\/London"
            },
            "location": {
                "id": "5057",
                "name": "Hall D, Crt 7",
                "type": "resource",
                "slug": "hall-d-crt-7",
                "venue_id": 90266,
                "venue_slug": "sugden-sports-centre"
            },
            "slot_display_location": "Hall D, Crt 7",
            "price": {
                "benefit_applied": false,
                "package_applied": false,
                "formatted": "\u00a39.00",
                "raw": 900
            },
            "starts_at": {
                "format_12_hour": "1:30pm",
                "format_24_hour": "13:30"
            },
            "ends_at": {
                "format_12_hour": "2:30pm",
                "format_24_hour": "14:30"
            },
            "last_bookable_at": {
                "format_12_hour": "1:35pm",
                "format_24_hour": "13:35"
            },
            "venue_name": "Sugden Sports Centre",
            "pricing_option_id": 992,
            "cart_type": "purchasableOccurrence",
            "composite_key": "276d8515",
            "booking": null,
            "bookings_count": 1,
            "spaces": 0,
            "capacity": 1,
            "action_to_show": {
                "status": "FULL",
                "reason": "The session being booked is already full"
            },
            "waitlist_id": null,
            "restrictions": {
                "pre_waiver": null,
                "pre_induction": null,
                "criteria": null
            },
            "has_pre_purchase_restrictions": false,
            "requires_induction": false,
            "restriction_ids": [],
            "benefit_available": null,
            "tags": []
        },
        {
            "id": "AQGbDqHG-fMFkilTTO3UJ5gD9-C9kfdu6A",
            "name": "Badminton 60min",
            "allows_anonymous_bookings": false,
            "pre_booking_notice": null,
            "root_activity_category": {
                "v2": true,
                "id": "01973a77-cc91-71b2-9a81-2dd265c72a35",
                "v2Id": "01973a77-cc91-71b2-9a81-2dd265c72a35",
                "name": "Badminton",
                "slug": "badminton",
                "v2_slug": "badminton",
                "v1_slug": null,
                "path": "badminton",
                "v1_type": null,
                "v2_type": null,
                "allocation_strategy": "customer",
                "image": "",
                "parent_slug": null,
                "has_children": false,
                "is_root": true
            },
            "category_slug": "badminton-60min",
            "duration": "60min",
            "instructors": [],
            "date": {
                "raw": "2026-02-09",
                "raw_pretty": "09\/02\/2026",
                "day_pretty": "Mon",
                "date_pretty": "9 Feb",
                "full_date_pretty": "Mon 09 February 2026",
                "full_date": "09 February 2026",
                "difference": "41 seconds ago",
                "tz": "Europe\/London"
            },
            "location": {
                "id": "5058",
                "name": "Hall D, Crt 8",
                "type": "resource",
                "slug": "hall-d-crt-8",
                "venue_id": 90266,
                "venue_slug": "sugden-sports-centre"
            },
            "slot_display_location": "Hall D, Crt 8",
            "price": {
                "benefit_applied": false,
                "package_applied": false,
                "formatted": "\u00a39.00",
                "raw": 900
            },
            "starts_at": {
                "format_12_hour": "1:30pm",
                "format_24_hour": "13:30"
            },
            "ends_at": {
                "format_12_hour": "2:30pm",
                "format_24_hour": "14:30"
            },
            "last_bookable_at": {
                "format_12_hour": "1:35pm",
                "format_24_hour": "13:35"
            },
            "venue_name": "Sugden Sports Centre",
            "pricing_option_id": 992,
            "cart_type": "purchasableOccurrence",
            "composite_key": "276d8515",
            "booking": null,
            "bookings_count": 0,
            "spaces": 1,
            "capacity": 1,
            "action_to_show": {
                "status": "BOOK",
                "reason": null
            },
            "waitlist_id": null,
            "restrictions": {
                "pre_waiver": null,
                "pre_induction": null,
                "criteria": null
            },
            "has_pre_purchase_restrictions": false,
            "requires_induction": false,
            "restriction_ids": [],
            "benefit_available": null,
            "tags": []
        }
    ]
}
```

add:

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
Invoke-WebRequest -UseBasicParsing -Uri "https://better-admin.org.uk/api/activities/cart/add" `
-Method "POST" `
-WebSession $session `
-Headers @{
"authority"="better-admin.org.uk"
  "method"="POST"
  "path"="/api/activities/cart/add"
  "scheme"="https"
  "accept"="application/json"
  "accept-encoding"="gzip, deflate, br, zstd"
  "accept-language"="en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7"
  "authorization"="Bearer v4.local.jLBnX3BI_OglWC6h5BDCUjTvNJIZ6upauBL27AXHDOKG5t5OcY5HkjpPOlEufvBZRGxc9yBh7slMS4EDGrVzxLO2v2yqrC8Gkfyvp4Jivt6YMbqZhSzvUwpQS7Lla1HKr4BqGclym7xortyqJLo1VIUJru91VfLJgzfZKMXZwGRTWqJAgVpf7Jf8Fnwezq_TO6BZzMqhIak7gnZ4hw"
  "origin"="https://bookings.better.org.uk"
  "priority"="u=1, i"
  "referer"="https://bookings.better.org.uk/location/sugden-sports-centre/badminton-60min/2026-02-20/by-time/slot/07:30-08:30/956478f9"
  "sec-ch-ua"="`"Google Chrome`";v=`"143`", `"Chromium`";v=`"143`", `"Not A(Brand`";v=`"24`""
  "sec-ch-ua-mobile"="?0"
  "sec-ch-ua-platform"="`"macOS`""
  "sec-fetch-dest"="empty"
  "sec-fetch-mode"="cors"
  "sec-fetch-site"="cross-site"
} `
-ContentType "application/json" `
-Body "{`"items`":[{`"id`":`"AQGbDtunTP1InFEHzkrYwLYEBgydlgabCA`",`"type`":`"purchasableOccurrence`",`"pricing_option_id`":992,`"apply_benefit`":true,`"activity_restriction_ids`":[]}],`"membership_user_id`":4620321,`"selected_user_id`":null}"
```



```json
{
    "data": {
        "id": 107288259,
        "source": "activity-booking",
        "total": 500,
        "formattedTotal": "\u00a35.00",
        "balance": 500,
        "formattedBalance": "\u00a35.00",
        "item_count": 1,
        "items": [
            {
                "id": 138365150,
                "cartable_id": 621451,
                "cartable_type": "av2Booking",
                "parent_item_id": null,
                "name": "Badminton 60min - Fri 20 Feb - 07:30",
                "membership_user_id": 4620321,
                "price": {
                    "benefit_applied": false,
                    "package_applied": false,
                    "formatted": "\u00a35.00",
                    "raw": 500
                },
                "user_friendly_type": "EloquentBooking",
                "enable_print_receipt": false,
                "cartable_resource": {
                    "id": "AQGbDtunTP1InFEHzkrYwLYEBgydlgabCA",
                    "name": "Badminton 60min",
                    "duration": "1h",
                    "venue_name": "Sugden Sports Centre",
                    "location": {
                        "id": "5052",
                        "name": "Hall C, Crt 2",
                        "type": "resource",
                        "slug": "hall-c-crt-2",
                        "venue_id": 90266,
                        "venue_slug": "sugden-sports-centre"
                    },
                    "date": {
                        "raw": "2026-02-20",
                        "raw_pretty": "20\/02\/2026",
                        "day_pretty": "Fri",
                        "date_pretty": "20 Feb",
                        "full_date_pretty": "Fri 20 February 2026",
                        "full_date": "20 February 2026",
                        "difference": "3 days from now",
                        "tz": "Europe\/London"
                    },
                    "starts_at": {
                        "format_12_hour": "7:30am",
                        "format_24_hour": "07:30"
                    },
                    "ends_at": {
                        "format_12_hour": "8:30am",
                        "format_24_hour": "08:30"
                    }
                },
                "sort_by": 0,
                "quantity": 1,
                "max_quantity": null,
                "notes": [],
                "child_items": [],
                "promotion_code": null
            }
        ],
        "payments": [],
        "uuid": "2c2dee0a-a146-457b-a7ec-97c5345c78ac",
        "credits": {
            "membership": {
                "type": "membership",
                "total_available": 0,
                "max_applicable": 0
            },
            "general": {
                "type": "general",
                "total_available": 0,
                "max_applicable": 0
            }
        },
        "attendeeWaiversRequired": false,
        "itemHash": "MTM4MzY1MTUw"
    }
}
```





## dom块：

时间页右上角的小login:

```http
<button data-testid="login" font-weight="700" color="#ffffff" class="Button__StyledButton-sc-5h7i9w-1 Button__OutlineButton-sc-5h7i9w-3 itCkpH cMwmPC LoginButton__StyledButton-sc-1kgkv36-0 eheRiY" type="button"><span class="Button__InnerWrapper-sc-5h7i9w-0 gluIKr">Log in</span></button>
```

Username:

```http
<input id="username" autocomplete="username" name="username" class="FormControl__StyledInput-sc-126vw6t-1 eoeHYU SharedLoginComponent__EmailInput-sc-hdtxi2-2 hCmrGX" value="" data-gtm-form-interact-field-id="0">
```

password:

```http
<input type="password" id="password" autocomplete="current-password" name="password" class="FormControl__StyledInput-sc-126vw6t-1 eoeHYU PasswordInput__StyledFormControl-sc-m5owcc-1 fIIWqQ" value="" data-gtm-form-interact-field-id="1">
```

Log in:

```http
<button type="submit" data-testid="log-in" class="Button__StyledButton-sc-5h7i9w-1 itCkpH SharedLoginComponent__LoginButton-sc-hdtxi2-5 gcsyMa">
	<span class="Button__InnerWrapper-sc-5h7i9w-0 gluIKr">Log&nbsp;in</span>
</button>
```



Time:

所有放出的时间都是class为"ClassCardComponent__ClassTime-sc-1v7d176-3 jJrPSZ"的dom块，具体时间是这些dom块的文本内容。

例如：

```http
<div class="ClassCardComponent__ClassTime-sc-1v7d176-3 jJrPSZ">15:00 - 15:40</div>
```

```http
document.querySelectorAll('div[class="ClassCardComponent__ClassTime-sc-1v7d176-3 jJrPSZ"]').length
```

Book:

例如：

```http
<div class="ContextualComponent__BookButton-sc-eu3gk6-2 ijPjsv">
	<a aria-label="Ad Hoc session Badminton 40min from 15:00 to 15:40" href="/location/moss-side-leisure-centre/badminton-40min/2026-02-11/by-time/slot/15:00-15:40/c1ce62a1">
		<button color="#418031" aria-hidden="true" tabindex="-1" type="button" class="Button__StyledButton-sc-5h7i9w-1 iEsZxq">
			<span class="Button__InnerWrapper-sc-5h7i9w-0 gluIKr">Book</span>
		</button>
	</a>
</div>
```

court selection:

```http
<div class="LocationSelectionComponent__LocationSelect-sc-q5qvqt-0 jrFsOT css-b62m3t-container"><span id="react-select-4-live-region" class="css-7pg0cj-a11yText"></span><span aria-live="polite" aria-atomic="false" aria-relevant="additions text" role="log" class="css-7pg0cj-a11yText"></span><div class=" css-iuumu2-control"><div class=" css-1fcjwlv"><div class=" css-atu4xv-singleValue">Main Hall Court 1</div><input id="react-select-4-input" tabindex="0" inputmode="none" aria-autocomplete="list" aria-expanded="false" aria-haspopup="true" aria-label="Select location" aria-required="true" role="combobox" aria-readonly="true" class="css-1hac4vs-dummyInput" value=""></div><div class=" css-1wy0on6"><div class=" css-86lqpf-indicatorContainer" aria-hidden="true"><svg data-prefix="fas" data-icon="chevron-down" class="svg-inline--fa fa-chevron-down" role="img" viewBox="0 0 448 512" aria-hidden="true"><path fill="currentColor" d="M201.4 406.6c12.5 12.5 32.8 12.5 45.3 0l192-192c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L224 338.7 54.6 169.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l192 192z"></path></svg></div></div></div></div>
```

```http
<div class="LocationSelectionComponent__LocationSelect-sc-q5qvqt-0 jrFsOT css-b62m3t-container"><span id="react-select-4-live-region" class="css-7pg0cj-a11yText"></span><span aria-live="polite" aria-atomic="false" aria-relevant="additions text" role="log" class="css-7pg0cj-a11yText"><span id="aria-selection">option Main Hall Court 1, selected.</span><span id="aria-focused">Main Hall Court 1 selected, 1 of 5.</span><span id="aria-results">5 results available.</span><span id="aria-guidance">Use Up and Down to choose options, press Enter to select the currently focused option, press Escape to exit the menu, press Tab to select the option and exit the menu.</span></span><div class=" css-1iflluj-control"><div class=" css-1fcjwlv"><div class=" css-atu4xv-singleValue">Main Hall Court 1</div><input id="react-select-4-input" tabindex="0" inputmode="none" aria-autocomplete="list" aria-expanded="true" aria-haspopup="true" aria-label="Select location" aria-required="true" role="combobox" aria-readonly="true" class="css-1hac4vs-dummyInput" value="" aria-controls="react-select-4-listbox"></div><div class=" css-1wy0on6"><div class=" css-3i48l5-indicatorContainer" aria-hidden="true"><svg data-prefix="fas" data-icon="chevron-down" class="svg-inline--fa fa-chevron-down" role="img" viewBox="0 0 448 512" aria-hidden="true"><path fill="currentColor" d="M201.4 406.6c12.5 12.5 32.8 12.5 45.3 0l192-192c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L224 338.7 54.6 169.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l192 192z"></path></svg></div></div></div><div class=" css-rtdkum-menu"><div class=" css-qr46ko" role="listbox" aria-multiselectable="false" id="react-select-4-listbox"><div class=" css-106ke05-option" aria-disabled="false" id="react-select-4-option-0" tabindex="-1" role="option">Main Hall Court 1</div><div class=" css-drblax-option" aria-disabled="false" id="react-select-4-option-1" tabindex="-1" role="option">FULL - Main Hall Court 2</div><div class=" css-drblax-option" aria-disabled="false" id="react-select-4-option-2" tabindex="-1" role="option">FULL - Main Hall Court 3</div><div class=" css-drblax-option" aria-disabled="false" id="react-select-4-option-3" tabindex="-1" role="option">FULL - Main Hall Court 4</div><div class=" css-drblax-option" aria-disabled="false" id="react-select-4-option-4" tabindex="-1" role="option">Main Hall Court 5</div></div></div></div>
```



Book now:

```http
<button type="button" class="Button__StyledButton-sc-5h7i9w-1 itCkpH"><span class="Button__InnerWrapper-sc-5h7i9w-0 gluIKr">Book now</span></button>
```



Add to basket:

```http
<button type="button" class="Button__StyledButton-sc-5h7i9w-1 Button__OutlineButton-sc-5h7i9w-3 itCkpH blBjjm"><span class="Button__InnerWrapper-sc-5h7i9w-0 gluIKr">Add to basket</span></button>
```



View basket:

https://bookings.better.org.uk/basket.



这里突然发现，如果没登录直接book或者add to basket，会直接跳出登陆窗口。