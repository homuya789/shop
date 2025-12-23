import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
import sqlite3, time, re

BASE = "https://domeggook.com"



# ---------- DB ----------
def setup_db():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_DIR = "/home/ys/shop/DB"
    DB_PATH = os.path.join(DB_DIR, "y1.db")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS y3 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT UNIQUE,   -- 상품번호 중복 방지
            title TEXT,
            price TEXT,
            min_qty TEXT,
            delivery_info TEXT,
            options TEXT,
            phone TEXT,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn



def save_product(conn, number, title, price, min_qty, delivery_info, options, phone):
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO y3 (number, title, price, min_qty, delivery_info, options, phone)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (number, title, price, min_qty, delivery_info, options, phone))

    conn.commit()
    print(f"💾 저장: {number} / {title} / {phone}")

# ---------- 유틸 ----------
def text_safe(driver, by, sel, timeout=5, default=""):
    try:
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, sel))
        )
        return el.text.strip()
    except:
        return default

def exists(driver, by, sel, timeout=3):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, sel))
        )
        return True
    except:
        return False

# ---------- 메인 로직(단일 루프, 같은 창만 사용) ----------
def run():
    conn = setup_db()
    
    options = webdriver.FirefoxOptions()
    options.headless = False  # 헤드리스 모드

    # geckodriver 경로 설정
    service = Service("/usr/local/bin/geckodriver")

    # Firefox 드라이버 실행
    driver = webdriver.Firefox(service=service, options=options)
    

    wait = WebDriverWait(driver, 10)

    try:
        # y1.db에서 YES 상품번호 조회
        y_conn = sqlite3.connect(DB_PATH)

        y_cur = y_conn.cursor()
        
        y_cur.execute("""
            SELECT number
            FROM y2
            WHERE yn='YES'
            AND number NOT IN (SELECT number FROM y3)
        """)


        yes_numbers = [row[0] for row in y_cur.fetchall()]
        y_conn.close()

        hrefs = [f"https://domeggook.com/{number}" for number in yes_numbers]
        print(f"대상: {len(hrefs)}개 (yn=YES)")


        for i, href in enumerate(hrefs, 1):
            try:
                driver.get(href)

                # 이미지 사용 가능 체크
                if exists(driver, By.CLASS_NAME, "lInfoViewImgUse", timeout=5):
                    txt = driver.find_element(By.CLASS_NAME, "lInfoViewImgUse").text.strip()
                    if "사용불가" in txt:
                        print(f"❌ [{i}] 이미지 사용 불가 - 건너뜀")
                        continue
                else:
                    print(f"❓ [{i}] 이미지 사용 여부 요소 없음 - 건너뜀")
                    continue

                # 배송비결제 UI면 스킵
                if exists(driver, By.CLASS_NAME, "lBtnSelectDeli", timeout=2):
                    print(f"❌ [{i}] 배송비결제 UI - 건너뜀")
                    continue
#-------------
                # ===== 상품번호 먼저 추출 =====
                try:
                    num_elem = driver.find_element(By.XPATH, '//div[@id="lInfoHeader"]/span[1]')
                    number = num_elem.text.replace("상품번호 :", "").strip()
                except:
                    number = f"no_num_{i}"

                title = text_safe(driver, By.ID, "lInfoItemTitle", timeout=8, default="제목 없음")

                # ===== 메인 사진 =====
                desc_elem_main = wait.until(EC.presence_of_element_located((By.ID, "lThumbImg")))
                soup_main = BeautifulSoup(desc_elem_main.get_attribute("outerHTML"), "html.parser")
                img_tags_main = soup_main.find_all("img")
                img_urls_main = [tag.get("src") for tag in img_tags_main if tag.get("src")]

                from bs4 import Comment
                sep_images_main = []
                for comment in soup_main.find_all(string=lambda text: isinstance(text, Comment)):
                    if "SEP" in comment:
                        next_elem = comment.find_next("img")
                        if next_elem:
                            sep_images_main.append(next_elem.get("src"))

                all_images_main = list(set(img_urls_main + sep_images_main))

                SAVE_DIR_MAIN = "p1"
                os.makedirs(SAVE_DIR_MAIN, exist_ok=True)
                for idx, url in enumerate(all_images_main, start=1):
                    try:
                        file_ext = os.path.splitext(url.split("?")[0])[1] or ".jpg"
                        file_path = os.path.join(SAVE_DIR_MAIN, f"{number}({idx}){file_ext}")
                        r = requests.get(url, timeout=10)
                        r.raise_for_status()
                        with open(file_path, "wb") as f:
                            f.write(r.content)
                        print(f"✅ 메인 사진 저장됨: {file_path}")
                    except Exception as e:
                        print(f"❌ 메인 사진 다운로드 실패 ({url}): {e}")

                # ===== 설명 사진 =====
                desc_elem_desc = wait.until(EC.presence_of_element_located((By.ID, "lInfoViewItemContents")))
                soup_desc = BeautifulSoup(desc_elem_desc.get_attribute("outerHTML"), "html.parser")
                img_tags_desc = soup_desc.find_all("img")
                img_urls_desc = [tag.get("src") for tag in img_tags_desc if tag.get("src")]

                sep_images_desc = []
                for comment in soup_desc.find_all(string=lambda text: isinstance(text, Comment)):
                    if "SEP" in comment:
                        next_elem = comment.find_next("img")
                        if next_elem:
                            sep_images_desc.append(next_elem.get("src"))

                all_images_desc = list(set(img_urls_desc + sep_images_desc))

                SAVE_DIR_DESC = "p2"
                os.makedirs(SAVE_DIR_DESC, exist_ok=True)
                for idx, url in enumerate(all_images_desc, start=1):
                    try:
                        file_ext = os.path.splitext(url.split("?")[0])[1] or ".jpg"
                        file_path = os.path.join(SAVE_DIR_DESC, f"{number}_desc({idx}){file_ext}")
                        r = requests.get(url, timeout=10)
                        r.raise_for_status()
                        with open(file_path, "wb") as f:
                            f.write(r.content)
                        print(f"✅ 설명 사진 저장됨: {file_path}")
                    except Exception as e:
                        print(f"❌ 설명 사진 다운로드 실패 ({url}): {e}")



                try:
                    amt_wrap = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "lInfoAmtWrap"))
                    )

                    # 1. 단일 가격 div 시도
                    try:
                        price_div = amt_wrap.find_element(By.CLASS_NAME, "lItemPrice")
                        price = price_div.text.strip()
                    except:
                        # 2. 가격표 table 시도
                        try:
                            price_table = amt_wrap.find_element(By.ID, "lAmtSectionTbl")
                            price = price_table.text.replace("\n", " / ").strip()
                        except:
                            price = "가격 정보 없음"
                except:
                    price = "가격 정보 없음"



                try:
                    box = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "lInfoItemContent"))
                    )
                    min_qty = box.find_element(By.TAG_NAME, "b").text.strip()
                except:
                    min_qty = "정보 없음"

                deli_period = text_safe(driver, By.CLASS_NAME, "lDeliPeriod", timeout=3, default="정보 없음")
                deli_method = text_safe(driver, By.CLASS_NAME, "lDeliMethod", timeout=3, default="정보 없음")
                pack_deli  = text_safe(driver, By.CLASS_NAME, "lPackDeli",  timeout=3, default="정보 없음")
                delivery_info = f"{deli_period}, {deli_method}, {pack_deli}"

                # 전체옵션보기 → onclick에서 팝업 URL 추출 → 같은 창에서 진입 후 back()
                options_text = "옵션 없음"
                try:
                    opt_a = driver.find_element(By.CSS_SELECTOR, "a.lBtnShowOptAll.lBtn")
                    onclick = opt_a.get_attribute("onclick") or ""
                    m = re.search(r"openWindow\('([^']+)'", onclick)
                    if m:
                        path = m.group(1)
                        option_url = urljoin(BASE, path)

                        driver.get(option_url)
                        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#itemOptAllViewTable tbody tr")))
                        rows = driver.find_elements(By.CSS_SELECTOR, "#itemOptAllViewTable tbody tr")

                        pairs = []
                        for row in rows:
                            tds = row.find_elements(By.TAG_NAME, "td")
                            if len(tds) >= 3:
                                ps = tds[1].text.strip()
                                pr = tds[2].text.strip()
                                pairs.append(f"{ps}:{pr}")
                        if pairs:
                            options_text = "; ".join(pairs)

                        driver.back()
                except:
                    pass  # 옵션 버튼/표 없으면 그대로 "옵션 없음"

                # 문의번호
                phone = "없음"
                try:
                    if exists(driver, By.ID, "lSellerInfo", timeout=5):
                        for th in driver.find_elements(By.CSS_SELECTOR, "#lSellerInfo th"):
                            if "문의번호" in th.text:
                                phone = th.find_element(By.XPATH, "following-sibling::td[1]").text.strip()
                                break
                except:
                    pass

                # 저장
                save_product(conn, number, title, price, min_qty, delivery_info, options_text, phone)

                time.sleep(0.2)  # 서버 예의상 소량 딜레이

            except Exception as e:
                print(f"❌ [{i}] 처리 오류: {e}")
                # 메인으로 복구 시도
                try:
                    driver.get("https://domeggook.com/main/item/itemPopular.php")
                except:
                    pass

    finally:
        driver.quit()
        conn.close()

if __name__ == "__main__":
    run()
