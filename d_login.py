from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import json
import time
def run():
    # Firefox 옵션 설정
    options = webdriver.FirefoxOptions()
    options.headless = False  # 헤드리스 모드

    # geckodriver 경로 설정
    service = Service("/usr/local/bin/geckodriver")  # geckodriver 경로 지정

    # Firefox 드라이버 실행
    driver = webdriver.Firefox(service=service, options=options)

    driver.get("https://domeggook.com/ssl/member/mem_loginForm.php")
    time.sleep(2)

    USER_ID = "dddzae04"
    USER_PW = "08Ah384949!@"

    driver.find_element(By.ID, "idInput").send_keys(USER_ID)
    driver.find_element(By.ID, "pwInput").send_keys(USER_PW)

    driver.find_element(By.CSS_SELECTOR, "input.formSubmit").click()
    time.sleep(5)

    if "로그아웃" in driver.page_source:
        print("✅ 로그인 성공")
    else:
        print("❌ 로그인 실패")
    #---------------
    cookies = driver.get_cookies()
    with open("do_cookies.json", "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)

    print("✅ 쿠키 저장 완료: domeggook_cookies.json")

    driver.quit()
