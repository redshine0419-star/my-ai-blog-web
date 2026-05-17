import requests
from requests.auth import HTTPBasicAuth
import os
import re
import time

# 제거할 HTML 패턴
# 내부 링크 섹션: 💡 연관 인사이트 포함 div
INTERNAL_LINK_RE = re.compile(
    r'\s*<div[^>]*>(?:(?!</div>).)*?💡\s*연관\s*인사이트(?:(?!</div>).)*?</div>\s*',
    re.DOTALL
)

# CTA 버튼: text-align:center + border-radius: 50px 포함 div
CTA_BUTTON_RE = re.compile(
    r'\s*<div[^>]*text-align\s*:\s*center[^>]*>(?:(?!</div>).)*?border-radius\s*:\s*50px(?:(?!</div>).)*?</div>\s*',
    re.DOTALL
)


def get_sites():
    return [
        {
            "name": "건강 포커스",
            "url": os.environ.get("SITE1_URL"),
            "user": os.environ.get("SITE1_USER"),
            "pass": os.environ.get("SITE1_PASS"),
        },
        {
            "name": "경제 트렌드",
            "url": os.environ.get("SITE2_URL"),
            "user": os.environ.get("SITE2_USER"),
            "pass": os.environ.get("SITE2_PASS"),
        },
        {
            "name": "넥스트 테크 웨이브",
            "url": os.environ.get("SITE3_URL"),
            "user": os.environ.get("SITE3_USER"),
            "pass": os.environ.get("SITE3_PASS"),
        },
    ]


def clean_content(raw):
    cleaned = INTERNAL_LINK_RE.sub('\n', raw)
    cleaned = CTA_BUTTON_RE.sub('\n', cleaned)
    return cleaned, cleaned != raw


def fetch_all_posts(base_url, auth):
    posts = []
    page = 1
    api = f"{base_url}/wp-json/wp/v2/posts"

    while True:
        resp = requests.get(api, auth=auth, params={"page": page, "per_page": 100, "context": "edit"}, timeout=30)
        if resp.status_code == 400:
            break  # 페이지 초과
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        posts.extend(batch)
        total_pages = int(resp.headers.get("X-WP-TotalPages", 1))
        if page >= total_pages:
            break
        page += 1

    return posts


def run(dry_run=True):
    sites = get_sites()

    for site in sites:
        print(f"\n{'='*55}")
        print(f"📌 [{site['name']}] 처리 시작")

        if not site["url"]:
            print("  ⚠️  환경변수 미설정 — 건너뜀")
            continue

        base_url = site["url"].split("/wp-json")[0]
        auth = HTTPBasicAuth(site["user"], site["pass"])

        try:
            posts = fetch_all_posts(base_url, auth)
        except Exception as e:
            print(f"  ❌ 포스트 조회 실패: {e}")
            continue

        print(f"  총 {len(posts)}개 글 확인")
        target_count = 0

        for post in posts:
            raw = post.get("content", {}).get("raw", "")
            cleaned, changed = clean_content(raw)

            if not changed:
                continue

            target_count += 1
            title = post.get("title", {}).get("raw", "")[:60]
            pid = post["id"]

            if dry_run:
                print(f"  [DRY-RUN] id={pid}  {title}")
            else:
                try:
                    resp = requests.post(
                        f"{base_url}/wp-json/wp/v2/posts/{pid}",
                        auth=auth,
                        json={"content": cleaned},
                        timeout=30
                    )
                    if resp.status_code == 200:
                        print(f"  ✅ 수정 완료  id={pid}  {title}")
                    else:
                        print(f"  ❌ 실패 ({resp.status_code})  id={pid}")
                except Exception as e:
                    print(f"  ❌ 오류  id={pid}: {e}")
                time.sleep(0.5)  # API 과부하 방지

        print(f"  → {target_count}개 글 {'대상 감지됨' if dry_run else '업데이트 완료'}")

    if dry_run:
        print("\n⚠️  Dry-run 모드입니다.")
        print("   실제 수정하려면:  DRY_RUN=false python update_existing_posts.py")


if __name__ == "__main__":
    dry_run = os.environ.get("DRY_RUN", "true").lower() != "false"
    run(dry_run=dry_run)
