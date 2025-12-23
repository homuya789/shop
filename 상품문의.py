import os
import json
import time
import sqlite3
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ===============================
# DB 설정
# ===============================
DB_DIR = "/home/ys/shop/DB"
DB_PATH = os.path.join(DB_DIR, "y1.db")
COOKIE_FILE = "do_cookies.json"


# ===============================
# DB 유틸
# ===============================
def get_product_numbers():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT number FROM y")
    rows = [row[0] for row in cur.fetchall()]
    conn.close()
    return rows


def delete_from_y(number):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM y WHERE number = ?", (number,))
    conn.commit()
    conn.close()
    print(f"🧹 y에서 삭제 완료: {number}")

# ✅ 세션 쿠키 저장/불러오기
def save_session_cookies(context):
    cookies = context.cookies()
    with open("do_cookies.json", "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)
    print("✅ 세션 쿠키 저장 완료")

def load_session_cookies(context):
    try:
        with open("do_cookies.json", "r", encoding="utf-8") as f:
            cookies = json.load(f)
        context.add_cookies(cookies)
        print("✅ 세션 쿠키 로드 완료")
    except FileNotFoundError:
        print("⚠️  세션 쿠키 파일이 없어 로그인 필요")


# ===============================
# 메인 로직
# ===============================
def login_and_write_inquiry(product_number):
    browser = None
    url = f"https://www.domeggook.com/{product_number}"
    print(f"\n▶ 상품번호 {product_number} 문의글 작성 시작")

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        context = browser.new_context()
        load_session_cookies(context)
        page = context.new_page()

        # 1️⃣ 도메인 접속
        page.goto("https://domeggook.com", wait_until="domcontentloaded")

        # 3️⃣ reload (로그인 적용 핵심)
        page.reload(wait_until="domcontentloaded")
        time.sleep(1)

        # 4️⃣ 상품 페이지 이동
        page.goto(url, wait_until="domcontentloaded")

        # 문의 탭
        page.click("a[href='#lTapSupport']")
        time.sleep(1)

        # ✅ supportIframe 대기
        page.wait_for_selector("#supportIframe", timeout=15000)
        iframe_element = page.query_selector("#supportIframe")
        frame = iframe_element.content_frame()
        print("✅ supportIframe 로드됨")

        # 문의글 작성 버튼
        frame.click("input[value='문의글 작성']")
        time.sleep(0.5)

        # ✅ 문의 작성 프레임 재선택
        page.wait_for_selector("iframe[name='supportIframe']", timeout=10000)
        iframe_element = page.query_selector("iframe[name='supportIframe']")
        frame = iframe_element.content_frame()

        # 체크박스 (있는 것만)
        checkbox_ids = [
            "lSupportWriteCheckbox",
            "lSupportWriteCheckbox2",
            "lSupportWriteCheckbox3",
            "lSupportWriteCheckbox4",
        ]

        for cb in checkbox_ids:
            sel = f"label[for='{cb}']"
            if frame.query_selector(sel):
                frame.click(sel)
                time.sleep(0.2)

        # 입력
        frame.fill("input[name=title]", "안녕하세요 리셀 문의드립니다!")
        frame.fill(
            "textarea[name=memo]",
            "안녕하세요 판매자님! 리셀 가능한지 문의드립니다!"
        )

        # confirm / alert 자동 승인
        page.on("dialog", lambda dialog: dialog.accept())

        # submit 클릭(등록)
        frame.click("input[type='submit']")


        time.sleep(1)
        return True

        # 등록 후 잠시 대기
        time.sleep(5)
        browser.close()
'''
    except KeyboardInterrupt:
        print("⛔ 사용자 중단 (Ctrl+C)")
        raise  # runner까지 같이 종료

    except PlaywrightTimeoutError as e:
        print(f"❌ 문의 실패 (타임아웃): {product_number} → {e}")
        return False

    except Exception as e:
        print(f"❌ 문의 실패: {product_number} → {e}")
        return False

    finally:
        if browser:
            browser.close()
'''

# ===============================
# run()
# ===============================
def run():
    numbers = get_product_numbers()

    for number in numbers:
        success = login_and_write_inquiry(number)

        if success:
            delete_from_y(number)
        else:
            print(f"⚠️ 재시도 대상 유지: {number}")

