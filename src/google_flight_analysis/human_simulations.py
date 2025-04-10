import random
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time

from config.logging import init_logger

logger = init_logger(__name__)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/98.0"
]


def random_wait(min_sec=1, max_sec=5):
    wait_time = random.uniform(min_sec, max_sec)
    logger.debug(f"Waiting {wait_time} seconds.")
    time.sleep(wait_time)


def simulate_scroll(driver, min_scrolls=1, max_scrolls=3):
    scrolls = random.randint(min_scrolls, max_scrolls)
    for _ in range(scrolls):
        scroll_distance = random.randint(100, 500)
        driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
        time.sleep(random.randint(0.1, 1))


def simulate_mouse_movement(driver, min_movements=3, max_movements=10):
    width = driver.execute_script("return window.innerWidth")
    height = driver.execute_script("return window.innerHeight")
    
    for _ in range(random.randint(5, 15)):  # Anzahl der Bewegungen
        x = random.randint(0, width)
        y = random.randint(0, height)
        ActionChains(driver).move_by_offset(x, y).perform()
        time.sleep(random.uniform(0.05, 0.3))


def get_user_agent():
    return random.choice(USER_AGENTS)
