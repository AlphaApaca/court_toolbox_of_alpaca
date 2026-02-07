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

目前阶段的如下问题：
目前比较合适的场馆有两个：sugden-sports-centre和moss-side-leisure-centre
每个场馆中，有多个羽毛球场地，但是不知道每天场官方会放出哪些时间段的羽毛球场地。
但是我可以简单梳理一下我期望的预定逻辑。
如果工作日（周一到周五）能有晚上的场地，最好预定晚上的（18点以后，包含18点开始的）。
如果是周六周天，那么上午9点以后开始的场地都可以预定，如果可用的时段很多，优先选连续的两个小时内场地最多的时段。
这其实给我一个启发，我能不能专门写一个函数来设计预定逻辑，来保证当我想改变我自己期望的时间段和场地时只需要改变这一个函数中的参数就可以？
如果要做到这一点，我应该在运行这个函数前就把所有可用预定（所有时间段的所有场地信息）全部获取到，

另外一个有趣的想法：业余羽毛球等级分制。