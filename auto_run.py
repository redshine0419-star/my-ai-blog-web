# V9.5: 수익 최적화 및 상업적 타겟팅 엔진
import requests
from requests.auth import HTTPBasicAuth
import google.generativeai as genai
import time, urllib.parse, os, feedparser

def get_realtime_commercial_keyword(api_key):
    rss_url = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    news_titles = [entry.title for entry in feed.entries[:12]]
    combined_titles = " | ".join(news_titles)
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # 1. 상업적 가치가 높은 키워드 추출 프롬프트 강화
    prompt = f"""다음 뉴스들 중에서 건강, 경제, 테크 블로그에서 '구매 결정'이나 '비용 비교'가 일어날 법한 고단가 키워드 1개를 선정해. 
    단순 정보성보다는 '솔루션 추천', '비용 분석', '트렌드 변화에 따른 수익 기회'와 연결될 수 있어야 해. 단어만 출력해.
    뉴스: {combined_titles}"""
    
    return model.generate_content(prompt).text.strip()

def run_auto_post_v9_5():
    # (환경변수 로드 및 설정 부분은 기존과 동일)
    secrets = get_env_secrets() 
    main_keyword = get_realtime_commercial_keyword(secrets["GEMINI_API_KEY"])
    print(f"💰 선정된 고단가 키워드: {main_keyword}")
    
    model = genai.GenerativeModel('gemini-2.5-flash')

    for site in secrets["SITES"]:
        try:
            # 2. 본문 생성 프롬프트 고도화 (시니어 기획자 피드백 반영)
            article_prompt = f"""키워드 [{main_keyword}]에 대해 {site['objective']}를 작성하되, 다음 구조를 엄격히 지켜:
            1. TITLE: 독자가 클릭하고 싶게 만드는 '상업적/정보적 가치'가 담긴 제목.
            2. 상단에 <blockquote>를 활용한 3줄 핵심 요약(TL;DR).
            3. [본문 첫 문단 뒤]: '함께 읽으면 수익이 되는 글' 추천 링크 자리 확보 (HTML 주석으로 표시).
            4. 중간에 2026년 예상 수치나 비교 데이터를 담은 <table>을 반드시 포함.
            5. 모바일 가독성을 위해 H2 태그 3개 이상, <ul> 리스트 활용.
            6. 마지막에 [전문가 Insight] 박스를 <div style="background:#f8f9fa; padding:15px;">로 감싸서 작성.
            """
            
            res = model.generate_content(article_prompt).text
            title = res.split("TITLE:")[1].split("\n")[0].strip() if "TITLE:" in res else f"[{main_keyword}] 관련 긴급 보고서"
            
            # 3. 광고 및 체류시간 증대 장치 이식
            internal_link = f'<div style="border:1px solid #eee; padding:15px; margin:20px 0;"><strong>📍 함께 보면 좋은 글:</strong> <a href="{site["url"].split("/wp-json")[0]}" style="color:{site["color"]};">2026년 {main_keyword} 시장 변화와 대응 전략</a></div>'
            cta_button = f'<div style="text-align:center; margin:40px 0;"><a href="{site["url"].split("/wp-json")[0]}" style="background:{site["color"]}; color:white; padding:18px 35px; border-radius:8px; text-decoration:none; font-weight:bold;">{site["cta_text"]}</a></div>'
            
            # 최종 본문 조립
            final_content = f'{res}\n{internal_link}\n{cta_button}'
            
            # (워드프레스 발행 로직 호출 - 기존과 동일)
            # ...
            print(f"✅ {site['name']} 수익 최적화 발행 완료")
            
        except Exception as e:
            print(f"❌ {site['name']} 실패: {e}")

if __name__ == "__main__":
    run_auto_post_v9_5()
