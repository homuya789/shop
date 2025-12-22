from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os


# === Firefox 프로필 경로 (고정) ===
PROFILE_PATH = "/home/ys/firefox_profiles/bunjang"
os.makedirs(PROFILE_PATH, exist_ok=True)

# === Firefox 옵션 ===
options = webdriver.FirefoxOptions()
options.headless = False  # GUI 모드

options.binary_location = "/opt/firefox/firefox"

# 최신 권장 방식: -profile 인자 사용
options.add_argument("-profile")
options.add_argument(PROFILE_PATH)

# (선택) 자동화 흔적 약간 줄이기
options.set_preference("dom.webdriver.enabled", False)
options.set_preference("useAutomationExtension", False)

# === geckodriver 경로 (Snap → 공식 설치) ===
service = Service("/usr/local/bin/geckodriver")
# 또는: service = Service()  # PATH 자동 탐색 (더 권장)
# === Firefox 실행 ===
driver = webdriver.Firefox(
    service=service,
    options=options
)

wait = WebDriverWait(driver, 15)

# === 번개장터 접속 ===
driver.get("https://bunjang.co.kr/")
time.sleep(2)

input("키")

# === 로그인 상태 확인 ===
try:
    wait.until(EC.presence_of_element_located((By.LINK_TEXT, "내상점")))
    print("✅ 이미 로그인 상태 (프로필 세션 유지됨)")
except:
    print("❌ 로그인 안됨 → 직접 로그인하세요")
    input("👉 로그인 완료 후 엔터 누르세요")

print("🚀 이후 자동화 코드 계속 실행 가능")

time.sleep(5)

# ❗ 종료해도 프로필 유지됨
driver.quit()
