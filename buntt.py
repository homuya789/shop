import os
import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# === 이미지 폴더 경로 지정 ===
P1_DIR = "/home/ys/shop/p1"  # 메인 이미지 폴더
P2_DIR = "/home/ys/shop/p2"  # 설명 이미지 폴더

def run():
    # === DB에서 상품 정보 읽기 ===

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_DIR = "/home/ys/shop/DB"
    DB_PATH = os.path.join(DB_DIR, "y1.db")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT number, title, price, min_qty, delivery_info, options
        FROM y3
    """)
    products = cursor.fetchall()
    if not products:
        print("⚠️ 업로드할 상품 없음 (y3 비어 있음)")
        return

    
    conn.close()

    # === 셀레니움 시작 ===

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
    '''
    # 탐지 우회 (JS 수준)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
            Object.defineProperty(navigator, 'languages', { get: () => ['ko-KR', 'en-US'] });
            window.chrome = { runtime: {} };
        """
    })
    '''


    # ✅ 번개장터 접속
    driver.get("https://bunjang.co.kr/")
    wait = WebDriverWait(driver, 10)
    time.sleep(2)
    print("시작합니다.")
    # ✅ 로그인 여부 확인 (내상점 버튼이 있으면 로그인 상태)
    try:
        my_shop = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "내상점")))
        print("✅ 자동 로그인 상태 유지됨")
    except:
        print("❌ 로그인 필요")
        input("🔑 로그인 완료 후 엔터")
    '''
    # ✅ 종료 대기
    input("엔터 누르면 브라우저 종료됨")
    driver.quit()
    '''

    try:
        # 텍스트로 접근해서 '판매하기' 링크 클릭
        sell_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '판매하기')]"))
        )
        sell_btn.click()
        print("✅ '판매하기' 버튼 클릭 성공")
    except Exception as e:
        print("❌ 클릭 실패:", e)
        time.sleep(2)
    print("판매하기 접속 완료")

    # === 상품 정보 입력 ===
    for number, title, price, min_qty, delivery_info, options in products:
        print(f"📦 상품 업로드 시작: {number} / {title}")

        # === 메인 이미지 업로드 ===
        main_images = [
            os.path.join(P1_DIR, f)
            for f in os.listdir(P1_DIR)
            if f.startswith(number) and f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]
        if not main_images:
            print(f"❌ 메인 이미지 없음: {number}")
        else:
            upload_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file'][accept*='image']"))
            )
            upload_input.send_keys("\n".join(main_images))
            print(f"✅ 메인 이미지 {len(main_images)}개 업로드")
    #사진 첨부는 최대 12장까지 됨
        # === 설명 이미지 업로드 ===
            desc_images = sorted([
                os.path.join(P2_DIR, f)
                for f in os.listdir(P2_DIR)
                if f.startswith(number) and f.lower().endswith(('.jpg', '.jpeg', '.png'))
            ])[:10] #10개 제한
            if desc_images:
                upload_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file'][accept*='image']"))
                )
                upload_input.send_keys("\n".join(desc_images))
                print(f"✅ 설명 이미지 {len(desc_images)}개 업로드")
            else:
                print(f"⚠ 설명 이미지 없음: {number}")




        # 상품명 입력
        title_box = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[placeholder*='상품명을 입력해 주세요.']")
            )
        )
        title_box.click()
        title_box.send_keys(title)

        # 가격 입력
        # 가격 입력 (+5000)
        try:
            # 문자열에서 숫자만 추출해서 정수 변환
            price_int = int(price.replace(",", "").replace("원", "").strip())
            price_int += 5000  # 5000원 추가
        except ValueError:
            price_int = 5000  # 가격이 없으면 5000원 기본값

        price_box = driver.find_element(By.CSS_SELECTOR, "input[placeholder='가격을 입력해 주세요.']")
        price_box.clear()
        price_box.send_keys(str(price_int))
        
        price_box.send_keys(Keys.TAB)
        time.sleep(0.3)
        (print("성공1"))


        # 카테고리 버튼 전체 로딩될 때까지 기다림
        buttons = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul li button"))
        )

        # "기타" 버튼 찾기
        target_btn = None
        for btn in buttons:
            if btn.text.strip() == "기타":
                target_btn = btn
                break

        if target_btn:
            # 화면에 보이도록 스크롤
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_btn)
            time.sleep(0.5)  # 스크롤 후 약간 대기

            # JS로 클릭 (오버레이나 가림 방지)
            driver.execute_script("arguments[0].click();", target_btn)
            print("✅ '기타' 클릭 성공")
        else:
            print("❌ '기타' 버튼을 못 찾음")


        (print("성공3"))




        # 평균출고일 줄바꿈 제거 + 양쪽 공백 정리
        delivery_info_clean = delivery_info.replace("\n", " ").strip()

        # 옵션은 쉼표(,) 기준 줄바꿈
        options_clean = options.replace(";", "\n")

        # 설명 입력
        desc_box = wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "textarea"))
        )
        desc_box.clear()
        desc_box.send_keys(f"배송정보: {delivery_info_clean}\n\n옵션:\n{options_clean}")
        print("성공4") 
        #time.sleep(30)
        s_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//label[contains(., '새 상품')]")
            )
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", s_btn
        )
        driver.execute_script("arguments[0].click();", s_btn)

         # React 상태 반영 대기 
        time.sleep(1.2)

        driver.execute_script("""
        document.querySelectorAll(
          "input[type='text'], input[type='number'], textarea"
        ).forEach(el => {
          el.dispatchEvent(new Event('blur', { bubbles: true }));
        });
        """)


        time.sleep(0.5)

        # 등록 버튼
        register_btn = driver.find_element(
            By.XPATH, "//button[normalize-space()='등록하기']"
        )
        time.sleep(1.5)
        driver.execute_script("arguments[0].click();", register_btn)

        print("✅ 등록 버튼 단일 클릭 완료")
        time.sleep(10)
        print(f"✅ {title} 업로드 완료")
    driver.quit()


    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # y2, y3 비우기
    cursor.execute("DELETE FROM y2")
    cursor.execute("DELETE FROM y3")

    conn.commit()
    conn.close()

    print("✅ y2, y3 초기화 완료")

if __name__ == "__main__":
    run()
