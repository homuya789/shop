from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
import sqlite3
import json
import re
import time
import os

def setup_db():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_DIR = "/home/ys/다운로드/DB"
    DB_PATH = os.path.join(DB_DIR, "d.db")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS del (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT UNIQUE
        )
    """)
    conn.commit()
    return conn
'''
# ✅ d.db 현재 경로 생성
def setup_db():
    conn = sqlite3.connect("d.db")  # DB 이름 d.db
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS del (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT UNIQUE
        )
    """)
    conn.commit()
    return conn
'''
# ✅ del 테이블에 number 저장
def insert_product(conn, number):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO del (number)
            VALUES (?)
        """, (number,))
        conn.commit()
        print(f"💾 del 저장 완료: {number}")
    except Exception as e:
        print(f"❌ del 저장 실패: {e}")


# ✅ 세션 쿠키 저장/불러오기
def save_session_cookies(driver):
    cookies = driver.get_cookies()
    with open("do_cookies.json", "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)
    print("✅ 세션 쿠키 저장 완료")

def load_session_cookies(driver):
    try:
        with open("do_cookies.json", "r", encoding="utf-8") as f:
            cookies = json.load(f)
        for cookie in cookies:
            if 'sameSite' in cookie:
                cookie.pop('sameSite')
            driver.add_cookie(cookie)
        print("✅ 세션 쿠키 로드 완료")
    except FileNotFoundError:
        print("⚠️ 세션 쿠키 파일이 없어 로그인 필요")


# ✅ 한 페이지 처리 (번호만 추출해서 del 테이블에 저장)
def process_current_page(driver, page_num, conn):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.lSupportList"))
        )
    except:
        print("❌ 항목이 없음 혹은 로그인 필요")
        return False

    items = driver.find_elements(By.CSS_SELECTOR, "li.lSupportList")
    print(f"🔍 총 항목 수: {len(items)}")

    for el in items:
        try:
            number_el = el.find_element(By.CSS_SELECTOR, ".lSupportNo")
            number = number_el.text.strip()
            insert_product(conn, number)  # del 테이블에 저장
            print(f"🔢 번호 추출 및 저장: {number}")
        except:
            continue

    return True

def get_total_pages(driver):
    try:
        span = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#lPage span"))
        )
        text = span.text  # 예: "총 2페이지"
        match = re.search(r'총\s*(\d+)\s*페이지', text)
        if match:
            total_pages = int(match.group(1))
            print(f"📄 총 {total_pages} 페이지 확인됨")
            return total_pages
    except:
        print("❌ 페이지 수 파싱 실패")
    return 1


# ✅ 전체 페이지 순회
def extract_all_pages():
    conn = setup_db()

    options = webdriver.FirefoxOptions()
    options.headless = False
    service = Service("/usr/local/bin/geckodriver") # geckodriver 경로

    driver = webdriver.Firefox(service=service, options=options)

    driver.get("https://domeggook.com/")
    time.sleep(2)

    load_session_cookies(driver)
    driver.refresh()
    time.sleep(2)

    driver.get("https://domeggook.com/main/myBuy/support/my_itemSupport.php?pg=1")
    time.sleep(2)

    # 1️⃣ 년도 선택
    select_year = Select(driver.find_element(By.NAME, "y1"))
    select_year.select_by_value("2024")  # 2024년 선택

    # 2️⃣ 검색 버튼 클릭
    search_btn = driver.find_element(By.ID, "lSupportSortSearch")
    search_btn.click()

    # 3️⃣ 검색 결과 기다리기
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.lSupportList"))
    )
    total_pages = get_total_pages(driver)

    for page_num in range(1, total_pages + 1):
        if page_num > 1:
            # 다음 페이지 버튼 클릭
            next_btn = driver.find_element(By.LINK_TEXT, str(page_num))
            next_btn.click()
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.lSupportList"))
            )
        print(f"\n📄 페이지 {page_num} 처리 중...")
        process_current_page(driver, page_num, conn)


    print("\n✅ 전체 페이지 순회 완료")
    save_session_cookies(driver)
    driver.quit()
    conn.close()

if __name__ == "__main__":
    extract_all_pages()

def run():
    extract_all_pages()

