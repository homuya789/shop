from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
import time, json
import os

# Firefox 옵션 설정
options = webdriver.FirefoxOptions()
options.headless = False  # 헤드리스 모드

# geckodriver 경로 설정
service = Service("/snap/bin/geckodriver")  # geckodriver 경로 지정

# Firefox 드라이버 실행
driver = webdriver.Firefox(service=service, options=options)

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

#driver.save_screenshot('3.png')
'''
# 팝업창으로 전환(필수)
WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

driver.switch_to.window(driver.window_handles[1])
print("페북 팝업 전환 완료")
'''
try:
    # 팝업창으로 전환(필수)
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

    driver.switch_to.window(driver.window_handles[1])
    print("페북 팝업 전환 완료")
    # email 입력 필드가 나타날 때까지 기다림
    email_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "email"))
    )
    email_box.send_keys("ydddzae04@gmail.com")

    print("아이디 입력 완료")

    #driver.save_screenshot('4.png')

    # --- 비밀번호 입력 ---
    email_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "pass"))
    )
    email_box.send_keys("08Ah384949!@")

    print("비번 입력 완료")

    #driver.save_screenshot('5.png')

    login_btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='login']"))
    )
    login_btn.click()

    print("로그인 버튼 클릭 완료")
except:
    print("이미 페북 로그인 상태 -> 로그인 생략")



time.sleep(5)
#driver.save_screenshot('6.png')
user_input = input("계속하려면 'go'를 입력하세요: ")

if user_input.lower() == "go":
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "btn_agree"))
    )
    submit_button.click()
    print("완료")
    time.sleep(3)
    #driver.save_screenshot('7.png')
else:
    print("입력이 'go'가 아니어서 다음 동작을 실행하지 않습니다.")

# ✅ 쿠키 저장
cookies = driver.get_cookies()
with open("bun_cookies.json", "w", encoding="utf-8") as f:
    json.dump(cookies, f, ensure_ascii=False, indent=2)

print("✅ 쿠키 저장 완료: do_cookies.json")

driver.quit()

