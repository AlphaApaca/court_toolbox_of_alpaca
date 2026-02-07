# 调度器模块，提供等待到指定时间的功能，适用于需要在特定时间点执行预订操作的场景
# Scheduler module that provides functionality to wait until a specified time, suitable for scenarios where booking operations need to be executed at specific time points.

import logging
import time
from datetime import datetime
from typing import Callable


logger = logging.getLogger(__name__)


def wait_until(target_time_str: str) -> None:
    """阻塞等待到指定时间（HH:MM:SS，今天）"""
    now = datetime.now()
    target = datetime.strptime(target_time_str, "%H:%M:%S").replace(
        year=now.year, month=now.month, day=now.day
    )
    if target < now:
        logger.warning("目标时间 %s 已经过，立即继续执行", target_time_str)
        return
    seconds = (target - now).total_seconds()
    logger.info("等待至 %s (约 %.1f 秒)", target_time_str, seconds)
    time.sleep(seconds)


def run_at(target_time_str: str, func: Callable, *args, **kwargs):
    wait_until(target_time_str)
    return func(*args, **kwargs)
