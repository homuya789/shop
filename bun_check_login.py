from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
import time, json
import os

# === Firefox 프로필 ===
PROFILE_PATH = "/home/ys/firefox_profiles/bunjang"
os.makedirs(PROFILE_PATH, exist_ok=True)

options = webdriver.FirefoxOptions()
options.headless = False
options.profile = PROFILE_PATH

service = Service("/usr/local/bin/geckodriver")

# Firefox는 딱 한 번만 생성
driver = webdriver.Firefox(
    service=service,
    options=options
)
#접속
driver.get("https://m.bunjang.co.kr/")
time.sleep(2)
print("접속")

#driver.save_screenshot('1.png')

WebDriverWait(driver, 10).until(
EC.presence_of_element_located((By.CSS_SELECTOR, "button.sc-dqBHgY.dDTfxq"))).click()
print("로그인 클릭")

#driver.save_screenshot('2.png')

WebDriverWait(driver, 10).until(
EC.presence_of_element_located((By.CSS_SELECTOR, "button.sc-gHboQg.blMWon"))).click()
print("페북 클릭")


try:
    # 팝업창으로 전환(필수)
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

    driver.switch_to.window(driver.window_handles[1])
    print("로그인 여부 확인중..")
        # email 입력 필드가 나타날 때까지 기다림
    email_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "email"))
    )
    print("로그인 안되있음. 로그인 필요함.")
except:
    print("로그인 되있음.")
driver.quit()
