#import d_login
#import 제외번호
#import 상품번호
#import 상품문의
import 문의여부
import 완
import buntt


def safe_run(name, func):
    print(f"\n=== {name} 실행 ===")
    try:
        func()
        print(f"✅ {name} 성공")
        return True
    except Exception as e:
        print(f"❌ {name} 실패")
        print(f"에러 원인: {e}")
        return False


print("===== 전체 실행 시작 =====")

steps = [
#    ("d_login", d_login.run),
#    ("제외번호", 제외번호.run),
#    ("상품번호", 상품번호.run),
#    ("상품문의", 상품문의.run),
    ("문의여부", 문의여부.run),
    ("완", 완.run),
    ("buntt", buntt.run),
]

for name, func in steps:
    safe_run(name, func)

print("\n===== 전체 실행 종료 =====")

