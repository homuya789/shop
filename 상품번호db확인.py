import sqlite3

# DB 파일 연결
conn = sqlite3.connect("y1.db")
cursor = conn.cursor()

# 테이블 전체 조회
cursor.execute("SELECT * FROM y")
rows = cursor.fetchall()

print("===== DB 전체 내용 =====")
for row in rows:
    print(row)

print(f"\n총 {len(rows)}개 레코드")
conn.close()

