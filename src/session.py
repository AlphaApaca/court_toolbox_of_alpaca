# 启动 Chrome，支持 user-data-dir/可复用 cookie 
# Launch Chrome with support for user-data-dir/reusable cookies
import logging
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from .config import AppConfig


logger = logging.getLogger(__name__)


def create_driver(config: AppConfig) -> webdriver.Chrome:
    opts = Options()
    if config.headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,900")

    profile_dir = Path(config.user_data_dir)
    profile_dir.mkdir(parents=True, exist_ok=True)
    opts.add_argument(f"--user-data-dir={profile_dir.resolve()}")

    logger.info("启动 Chrome，headless=%s，profile=%s", config.headless, profile_dir)
    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(config.timeout_seconds)
    driver.implicitly_wait(2)
    return driver
