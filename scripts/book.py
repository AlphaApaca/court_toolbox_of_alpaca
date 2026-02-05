#!/usr/bin/env python3
import argparse
import logging
import sys

from src.auth import ensure_logged_in
from src.booking import run_booking
from src.config import AppConfig
from src.scheduler import run_at
from src.session import create_driver


def parse_args():
    parser = argparse.ArgumentParser(description="Better UK 场馆自动预约")
    parser.add_argument("--headless", action="store_true", help="强制 headless 模式运行")
    parser.add_argument("--no-headless", action="store_true", help="强制关闭 headless")
    parser.add_argument("--polling-start", type=str, help="轮询/开抢起始时间，格式 HH:MM:SS")
    parser.add_argument("--dry-run", action="store_true", help="演练模式，仅走流程不等待 22:00")
    return parser.parse_args()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    args = parse_args()
    config = AppConfig()

    if args.headless:
        config.headless = True
    if args.no_headless:
        config.headless = False
    if args.polling_start:
        config.polling_start = args.polling_start

    try:
        config.validate()
    except ValueError as exc:
        logging.error("配置错误: %s", exc)
        sys.exit(1)

    driver = create_driver(config)
    try:
        ensure_logged_in(driver, config)
        if args.dry_run:
            logging.info("演练模式，直接执行预约流程")
            run_booking(driver, config)
        else:
            logging.info("等待到开抢时间: %s", config.polling_start)
            run_at(config.polling_start, run_booking, driver, config)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
