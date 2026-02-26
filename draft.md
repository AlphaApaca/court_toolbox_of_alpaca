todo: 测试定时订场，多账号并行同时测试

# 基本信息

登陆URL: https://bookings.better.org.uk/location/sugden-sports-centre
https://bookings.better.org.uk/location/moss-side-leisure-centre

book URL: https://bookings.better.org.uk/location/sugden-sports-centre/badminton-60min/2026-01-13/by-time

### 4. others

另外一个有趣的想法：业余羽毛球等级分制。(画大饼) （可能是下一个项目？）

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