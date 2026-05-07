import requests
from requests.auth import HTTPBasicAuth
import google.generativeai as genai
import time
import urllib.parse
import os

# GitHub Secrets에서 환경변수 로드
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
# 도메인 정보 (GitHub Secrets에 등록된 값을 가져옴)
# ... (중략: 기존 blogs 설정 로직과 동일하게 os.environ으로 구성) ...

def run_auto_post():
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # 1. 오늘의 자동 키워드 추출 (2026년 최신 트렌드 기반)
    keyword_res = model.generate_content("2026년 현재 사람들이 가장 관심 있어 할 건강, 경제, 테크 통합 키워드 하나만 단어로 추천해줘.")
    main_keyword = keyword_res.text.strip()
    
    print(f"🎯 오늘의 타겟 키워드: {main_keyword}")

    # 2. 블로그별 순차 발행
    for site_name, config in blogs.items():
        try:
            # (기존 V8.1의 썸네일 생성, 본문 작성, 발행 로직 수행)
            # ... 코드 생략 (기존 로직과 동일) ...
            print(f"✅ {site_name} 발행 완료")
            time.sleep(30) # 안전을 위한 간격
        except Exception as e:
            print(f"❌ {site_name} 실패: {e}")

if __name__ == "__main__":
    run_auto_post()