# 상품번호만 추출 + sqlite3 저장
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import sqlite3
import json
import time

print("현재 작업 디렉토리:", os.getcwd())

# DB
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = "/home/ys/shop/DB"
DB_PATH = os.path.join(DB_DIR, "y1.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS y (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number TEXT UNIQUE
    )
""")
conn.commit()

def get_excluded_numbers():
    DB_PATH1 = os.path.join(DB_DIR, "d.db")
    conn = sqlite3.connect(DB_PATH1)
    cursor = conn.cursor()
    cursor.execute("SELECT number FROM del")
    excluded = set(row[0] for row in cursor.fetchall())
    conn.close()
    return excluded


# Firefox 옵션 설정
options = webdriver.FirefoxOptions()
options.headless = False  # 헤드리스 모드

# geckodriver 경로 설정
service = Service("/usr/local/bin/geckodriver")

# Firefox 드라이버 실행
driver = webdriver.Firefox(service=service, options=options)

driver.get("https://domeggook.com/main/item/itemPopular.php")  # 반드시 도메인 먼저 열어야 쿠키 추가 가능
wait = WebDriverWait(driver, 10)


# ✅ 저장된 쿠키 불러오기
'''
COOKIE_FILE = "/home/ys/다운로드/do_cookies.json"
with open("do_cookies.json", "r", encoding="utf-8") as f:
    cookies = json.load(f)

for cookie in cookies:
    # domain 키가 없으면 추가
    if "domain" not in cookie:
        cookie["domain"] = ".domeggook.com"
    try:
        driver.add_cookie(cookie)
    except Exception as e:
        print("쿠키 추가 실패:", cookie, e)

driver.refresh()  # 새로고침해서 로그인 반영
time.sleep(2)
'''
def run():
    excluded = get_excluded_numbers()
    print("✅ 제외 번호 불러옴:", excluded)
    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".topBigLi, .topMiddleLi, .topSmallLi")))
        items = driver.find_elements(By.CSS_SELECTOR, ".topBigLi, .topMiddleLi, .topSmallLi")

        # ✅ 1~150위까지 20개씩 끊어서 긁기
        for start in range(0, 150, 20):
            end = start + 20
            href_list = []
            
            for item in items[start:end]:  # start~end 구간만
                try:
                    a_tag = item.find_element(By.TAG_NAME, "a")
                    href = a_tag.get_attribute("href")
                    if href:
                        href_list.append(href)
                except:
                    continue

            for idx, href in enumerate(href_list, start=start+1):
                try:
                    driver.execute_script("window.open(arguments[0]);", href)
                    driver.switch_to.window(driver.window_handles[1])

                    # ✅ 이미지 사용 가능 여부 확인
                    try:
                        image_permission_elem = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "lInfoViewImgUse"))
                        )
                        if "사용불가" in image_permission_elem.text.strip():
                            print(f"❌ [{idx+1}] 이미지 사용 불가 상품 - 건너뜀")
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                            continue
                    except:
                        print(f"❓ [{idx+1}] 이미지 사용 여부 요소 없음 - 건너뜀")
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        continue

                    # ✅ 배송비결제 UI 확인
                    try:
                        driver.find_element(By.CLASS_NAME, "lBtnSelectDeli")
                        print(f"❌ [{idx+1}] 배송비결제 UI 있는 상품 - 건너뜀")
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        continue
                    except:
                        pass  # 없으면 통과

                    # ✅ 상품번호 추출
                    try:
                        lInfoHeader = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.ID, "lInfoHeader"))
                        )
                        span_text = lInfoHeader.find_element(By.TAG_NAME, "span").text.strip()

                        if "상품번호" in span_text:
                            y = span_text.split(":")[1].strip()
                        else:
                            y = "없음"

                        print(f"✅ [{idx+1}] 상품번호: {y}")

                        # ✅ DB 저장 (제외 상품 건너뜀)
                        if y not in excluded:
                            try:
                                cursor.execute("INSERT OR IGNORE INTO y (number) VALUES (?)", (y,))
                                conn.commit()
                            except Exception as db_err:
                                print(f"❌ DB 저장 실패: {db_err}")
                        else:
                            print(f"⏭️ 제외된 상품번호 {y} - DB 저장 안 함")

                    except Exception as e:
                        print(f"❌ [{idx+1}] 상품번호 추출 실패:", e)

                    # ✅ 탭 닫고 복귀
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                except Exception as e:
                    print(f"❌ [{idx+1}] 상품 처리 중 오류:", e)
                    if len(driver.window_handles) > 1:
                        driver.switch_to.window(driver.window_handles[0])

    except Exception as e:
        print("❌ 메인 페이지 로딩 실패:", e)

    driver.quit()
    conn.close()

if __name__ == "__main__":
    run()
