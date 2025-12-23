for item_data in items_data:
    idx = item_data["index"]

    # 1️⃣ 답변대기 → 출력만 하고 스킵
    if "답변완료" not in item_data["status"]:
        print(f"⚪ 답변대기 항목 (#{idx+1})")
        continue

    # 2️⃣ 답변완료만 여기로 내려옴
    print(f"\n🟢 답변완료 항목 발견 (#{idx+1})")

    # 👉 반드시 클릭
    current_item = page.query_selector_all("li.lSupportList")[idx]
    current_item.click()

    try:
        page.wait_for_selector(".lSupportAnswer", timeout=5000)
        answer_area = page.query_selector(".lSupportAnswer")
    except:
        answer_area = None

    if not answer_area:
        print("❌ 답변 내용 로딩 실패 (타임아웃)")
        continue

    answer_text = answer_area.inner_text()
    print(f"🔍 답변 내용:\n{answer_text}")

    result = is_resell_allowed(answer_text)
    print(f"🧠 판별 결과: {result}")

    if result.upper() in ["YES", "NO"]:
        match = re.search(r'domeggook\.com/(\d+)', item_data["href"])
        if match:
            insert_product(conn, match.group(1), result)
        else:
            print("❌ 상품 번호 추출 실패")
