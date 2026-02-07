# 登录及会话检测
# Login and session detection
import logging
from typing import Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .config import AppConfig
from . import locators


logger = logging.getLogger(__name__)


def _wait(driver, locator: str, timeout: int):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, locator)))


def login(driver, config: AppConfig, login_url: Optional[str] = None) -> None:
    url = login_url or f"{config.base_url}login"
    logger.info("打开登录页: %s", url)
    driver.get(url)

    try:
        email_input = _wait(driver, locators.LOGIN_EMAIL, config.timeout_seconds)
        password_input = _wait(driver, locators.LOGIN_PASSWORD, config.timeout_seconds)
    except TimeoutException as exc:
        raise RuntimeError("未在登录页找到邮箱/密码输入框，需检查选择器或 URL") from exc

    email_input.clear()
    email_input.send_keys(config.email)
    password_input.clear()
    password_input.send_keys(config.password)

    submit = driver.find_element(By.CSS_SELECTOR, locators.LOGIN_SUBMIT)
    submit.click()

    logger.info("登录提交完成，等待跳转")
    WebDriverWait(driver, config.timeout_seconds).until(EC.url_changes(url))


def ensure_logged_in(driver, config: AppConfig, login_url: Optional[str] = None) -> None:
    # 简单检测：如果页面存在登录按钮，则执行登录；否则假定 session 可用。
    try:
        driver.get(config.base_url)
        WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))
        login_buttons = driver.find_elements(By.CSS_SELECTOR, locators.LOGIN_SUBMIT)
        if login_buttons:
            logger.info("检测到可能需要登录，开始登录流程")
            login(driver, config, login_url=login_url)
        else:
            logger.info("已登录或可重用 cookie，会话检测通过")
    except Exception as exc:  # noqa: BLE001
        logger.warning("会话检测出现异常，尝试重新登录: %s", exc)
        login(driver, config, login_url=login_url)