import logging
from datetime import datetime, timedelta
from typing import Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .config import AppConfig
from . import locators


logger = logging.getLogger(__name__)


def _wait_clickable(driver, locator: str, timeout: int):
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, locator)))


def compute_target_date(days_ahead: int) -> datetime:
    return datetime.now().date() + timedelta(days=days_ahead)


def select_venue(driver, config: AppConfig) -> None:
    # 根据实际 DOM 调整选择器，目前为占位实现
    logger.info("选择场馆: %s", config.venue_name)
    search_box = _wait_clickable(driver, locators.VENUE_SEARCH_INPUT, config.timeout_seconds)
    search_box.clear()
    search_box.send_keys(config.venue_name)
    WebDriverWait(driver, config.timeout_seconds).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, locators.VENUE_RESULT_ITEM))
    )
    results = driver.find_elements(By.CSS_SELECTOR, locators.VENUE_RESULT_ITEM)
    if not results:
        raise RuntimeError("未找到场馆搜索结果，请检查选择器或场馆名称")
    results[0].click()


def open_target_date(driver, config: AppConfig, date_obj) -> None:
    logger.info("打开目标日期: %s", date_obj)
    picker = _wait_clickable(driver, locators.DATE_PICKER, config.timeout_seconds)
    picker.click()
    # 这里需结合实际日期选择器实现，目前假定可直接输入
    try:
        picker.clear()
        picker.send_keys(date_obj.strftime("%Y-%m-%d"))
    except Exception:
        logger.debug("日期控件不可直接输入，后续需要补充具体点击逻辑")


def pick_time_slot(driver, preferred_times, timeout: int) -> Optional[str]:
    WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, locators.TIME_SLOT))
    )
    slots = driver.find_elements(By.CSS_SELECTOR, locators.TIME_SLOT)
    if not slots:
        logger.warning("未发现任何时间槽")
        return None

    for pref in preferred_times:
        for slot in slots:
            if pref in slot.text:
                slot.click()
                logger.info("已选择时间槽: %s", pref)
                return pref
    # 如果没有偏好匹配，选择第一个可用
    slots[0].click()
    logger.info("未匹配到偏好时间，选择第一个可用时间槽: %s", slots[0].text)
    return slots[0].text


def add_to_basket(driver, timeout: int) -> None:
    button = _wait_clickable(driver, locators.ADD_TO_BASKET, timeout)
    button.click()
    logger.info("已加入购物车，未自动支付")


def run_booking(driver, config: AppConfig) -> None:
    target_date = compute_target_date(config.target_days_ahead)
    driver.get(config.base_url)

    select_venue(driver, config)
    open_target_date(driver, config, target_date)

    try:
        chosen = pick_time_slot(driver, config.preferred_times, config.timeout_seconds)
        if not chosen:
            raise RuntimeError("没有找到合适的时间槽")
        add_to_basket(driver, config.timeout_seconds)
        logger.info("流程完成，已将 %s 加入购物车", chosen)
    except TimeoutException as exc:
        raise RuntimeError("在选择或加入购物车时超时，需检查选择器和页面流程") from exc
