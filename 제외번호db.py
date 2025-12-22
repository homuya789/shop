import sqlite3

# 1️⃣ DB 연결
conn = sqlite3.connect("d.db")
cursor = conn.cursor()

# 2️⃣ del 테이블 데이터 조회
cursor.execute("SELECT * FROM del")  # 테이블 이름이 'del'이라 가정
rows = cursor.fetchall()

# 3️⃣ 출력
if rows:
    print("📄 del 테이블 내용:")
    for row in rows:
        print(row)
else:
    print("⚠️ del 테이블에 데이터가 없습니다.")

# 4️⃣ 연결 종료
conn.close()

