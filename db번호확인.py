import sqlite3

# DB 연결
conn = sqlite3.connect("y1.db")
cursor = conn.cursor()

# 테이블 존재 여부 확인
cursor.execute("""
    SELECT name FROM sqlite_master
    WHERE type='table' AND name='y'
""")
table_exists = cursor.fetchone()

if not table_exists:
    print("❌ 'y' 테이블이 없습니다.")
else:
    # DB 내용 확인
    cursor.execute("SELECT id, number FROM y")
    rows = cursor.fetchall()

    if not rows:
        print("⚠️ DB에 저장된 상품번호가 없습니다.")
    else:
        print(f"📦 저장된 상품번호 {len(rows)}개:")
        for row in rows:
            print(f"ID: {row[0]}, 상품번호: {row[1]}")

# 연결 종료
conn.close()
