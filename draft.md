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

### 2. 预定逻辑实现

如果工作日（周一到周五）能有晚上的场地，最好预定晚上的（18点以后，包含18点开始的）。
如果是周六周天，那么上午9点以后开始的场地都可以预定，如果可用的时段很多，优先选连续的两个小时内场地最多的时段。
这其实给我一个启发，我能不能专门写一个函数来设计预定逻辑，来保证当我想改变我自己期望的时间段和场地时只需要改变这一个函数中的参数就可以？
如果要做到这一点，我应该在运行这个函数前就把所有可用预定（所有时间段的所有场地信息）全部获取到，

### 3. 两个预定时间不定放出

并且，每个场馆（sugden和moss side）的可选预定时间都有两个badminton-60min和badminton-40min。对于badminton-60min，一般要订到至少连续的2h（两个预定），最多4h（四个预定）（如果后面有机会延续富贵杯）。对于badminton-40min，一般要订到连续的2h（三个预定）最多4h（六个预定）。最好有几个账号并行预定，

### 4. others

另外一个有趣的想法：业余羽毛球等级分制。(画大饼)

# dom块：

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
<button type="submit" data-testid="log-in" class="Button__StyledButton-sc-5h7i9w-1 itCkpH SharedLoginComponent__LoginButton-sc-hdtxi2-5 gcsyMa"><span class="Button__InnerWrapper-sc-5h7i9w-0 gluIKr">Log&nbsp;in</span></button>
```



Time:

所有放出的时间都是class为"ClassCardComponent__ClassTime-sc-1v7d176-3 jJrPSZ"的dom块，具体时间是这些dom块的文本内容。

```http
<div class="ClassCardComponent__ClassTime-sc-1v7d176-3 jJrPSZ">15:00 - 15:40</div>
```

```http
document.querySelectorAll('div[class="ClassCardComponent__ClassTime-sc-1v7d176-3 jJrPSZ"]').length
```



Book:

```http
<div class="ContextualComponent__BookButton-sc-eu3gk6-2 ijPjsv"><a aria-label="Ad Hoc session Badminton 40min from 15:00 to 15:40" href="/location/moss-side-leisure-centre/badminton-40min/2026-02-11/by-time/slot/15:00-15:40/c1ce62a1"><button color="#418031" aria-hidden="true" tabindex="-1" type="button" class="Button__StyledButton-sc-5h7i9w-1 iEsZxq"><span class="Button__InnerWrapper-sc-5h7i9w-0 gluIKr">Book</span></button></a></div>
```



location selection:

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