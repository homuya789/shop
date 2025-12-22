from selenium.webdriver.firefox.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
import time, json, os

options = webdriver.FirefoxOptions()
#options.add_argument("--headless=new")  # GUI 없이 실행
# Firefox 옵션 설정

# geckodriver 경로 설정
service = Service("/snap/bin/geckodriver")  # geckodriver 경로 지정

# Firefox 드라이버 실행
driver = webdriver.Firefox(service=service, options=options)

'''
stealth(driver,
        languages=["ko-KR", "ko"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
)
'''

driver.get("https://domeggook.com/")
time.sleep(2)

if os.path.exists("do_cookies.json"):
    with open("do_cookies.json", "r", encoding="utf-8") as f:
        cookies = json.load(f)

    for cookie in cookies:
        cookie.pop("sameSite", None)
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            pass

    driver.refresh()
    time.sleep(3)

    if "로그아웃" in driver.page_source:
        print("로그인 유지 확인됨")
    else:
        print("로그인 안됨")
else:
    print("쿠키 파일 없음")

driver.quit()

