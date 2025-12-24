import sqlite3
import os
import json
import re
import time
from playwright.sync_api import sync_playwright

# ✅ 답변 내용 키워드로 리셀 가능 여부 판단
def is_resell_allowed(answer_text: str) -> str:
    text = answer_text.lower()
    if any(keyword in text for keyword in ["가능", "됩니다", "하셔도", "괜찮", "판매하세요"]):
        return "YES"
    elif any(keyword in text for keyword in ["불가", "안됨", "어렵", "불가능", "금지", "안됩니다"]):
        return "NO"
    else:
        return "NO"

# ✅ y2 테이블 생성
def setup_db():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_DIR = "/home/ys/shop/DB"
    DB_PATH = os.path.join(DB_DIR, "y1.db")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # y2 생성: number는 y와 동일, yn은 YES/NO
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS y2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT UNIQUE,
            yn TEXT
        )
    """)
    conn.commit()
    return conn

# ✅ y2에 저장
def insert_product(conn, number, yn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO y2 (number, yn)
            VALUES (?, ?)
            ON CONFLICT(number) DO UPDATE SET yn=excluded.yn
        """, (number, yn))
        conn.commit()
        print(f"💾 y2 저장 완료: {number} ({yn})")
    except Exception as e:
        print(f"❌ y2 저장 실패: {e}")



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

# ✅ 총 페이지 수 가져오기
def get_total_pages(page):
    try:
        page.wait_for_selector("#lPage span", timeout=5000)
        text = page.query_selector("#lPage span").inner_text()  # 예: "총 2페이지"
        match = re.search(r'총\s*(\d+)\s*페이지', text)
        if match:
            total_pages = int(match.group(1))
            print(f"📄 총 {total_pages} 페이지 확인됨")
            return total_pages
    except Exception as e:
        print(f"❌ 페이지 수 파싱 실패: {e}")
    return 1

# ✅ 한 페이지 처리
def process_current_page(page, page_num, conn):
    try:
        page.wait_for_selector("li.lSupportList", timeout=10000)
    except:
        print("❌ 항목이 없음 혹은 로그인 필요")
        return False

    raw_items = page.query_selector_all("li.lSupportList")
    print(f"🔍 총 문의 항목 수: {len(raw_items)}")

    # 클릭 전에 필요한 데이터 미리 추출
    items_data = []
    for idx, el in enumerate(raw_items):
        status = el.query_selector(".lSupportStatus").inner_text()
        question = el.query_selector(".lSupportMemo").inner_text()
        a_tag = el.query_selector("a")
        href = a_tag.get_attribute("href") if a_tag else ""
        items_data.append({
            "status": status,
            "question": question,
            "href": href,
            "index": idx
        })

    found = False
    for item_data in items_data:
        if "답변완료" in item_data["status"]:  
            found = True
            print(f"\n🟢 답변완료 항목 발견 (#{item_data['index']+1})")

            try:
                page.wait_for_selector("li.lSupportList .lSupportMemo", timeout=5000)
                answer_area = page.query_selector(".lSupportMemo")
            except:
                answer_area = None

            if answer_area:
                answer_text = answer_area.inner_text()
                print(f"🔍 답변 내용:\n{answer_text}")

                result = is_resell_allowed(answer_text)
                print(f"🧠 판별 결과: {result}")

                if result.upper() in ["YES", "NO"]:
                    match = re.search(r'domeggook\.com/(\d+)', item_data["href"])
                    if match:
                        product_number = match.group(1)
                        insert_product(conn, product_number, result)
                    else:
                        print("❌ 상품 번호 추출 실패")
            else:
                print("❌ 답변 대기(타임아웃)")
            
        else:
            print("⚪ 답변대기 항목")

    return found




# ✅ 전체 페이지 순회
def extract_all_pages():
    conn = setup_db()

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        context = browser.new_context()

        # ✅ 쿠키 먼저 로드 (여기서 들여쓰기 Space 4칸)
        load_session_cookies(context)

        page = context.new_page()

        # ✅ 홈 먼저 열고 새로고침 (쿠키 적용 확인)
        page.goto("https://domeggook.com/", wait_until="domcontentloaded")
        page.reload()
        time.sleep(2)


        # ✅ 이제 마이페이지 접근
        page.goto("https://domeggook.com/main/myBuy/support/my_itemSupport.php?pg=1", wait_until="domcontentloaded")
        total_pages = get_total_pages(page)

        for page_num in range(1, total_pages + 1):
            url = f"https://domeggook.com/main/myBuy/support/my_itemSupport.php?pg={page_num}"
            page.goto(url, wait_until="domcontentloaded")
            print(f"\n📄 페이지 {page_num} 처리 중...")

            process_current_page(page, page_num, conn)
            time.sleep(1)

        print("\n✅ 전체 페이지 순회 완료")
        save_session_cookies(page.context)
        browser.close()
        conn.close()
    
def run():
    extract_all_pages()

if __name__ == "__main__":
    run()

