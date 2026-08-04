"""
Task 2 — Crawl bài viết review/kinh nghiệm du lịch từ blogger cho 10 tỉnh miền Bắc.

Chủ đề: Trợ Lý Hướng Dẫn Viên Du Lịch Thông Minh (SUGGESTED_TOPICS.md, mục 5).
Nguồn: mỗi tỉnh 1 bài "kinh nghiệm/lịch trình/ẩm thực" từ blogger hoặc trang du lịch uy tín
(mia.vn, ivivu.com/blog, vntrip.vn, pystravel.vn, hoangviettravel.vn) — khác domain/bài
với cẩm nang tổng quan ở Task 1 để tạo góc nhìn bổ sung (lịch trình cụ thể, ẩm thực, mẹo
tiết kiệm chi phí — đúng loại câu hỏi mẫu trong đề bài).

Cách làm: dùng `requests` + `BeautifulSoup` thay vì Crawl4AI/Playwright — các trang này
đều server-render nội dung (không cần chạy JS thật để lấy text), nên requests đơn giản,
nhanh và không cần cài thêm Chromium. (klook.com chặn bot bằng Cloudflare -> trả 403, đã
loại khỏi danh sách và thay bằng nguồn tương đương hoạt động.)
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RAGLabBot/1.0"}


def setup_directory():
    """Tạo thư mục data/landing/news/ nếu chưa có."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


ARTICLE_URLS = [
    "https://mia.vn/cam-nang-du-lich/thuong-thuc-10-mon-ngon-nhat-cua-am-thuc-o-pho-co-ha-noi-2927",
    "https://www.vntrip.vn/cam-nang/du-lich-ha-giang-tu-tuc-3-ngay-2-dem-3047",
    "https://hoangviettravel.vn/du-lich-ninh-binh/",
    "https://www.ivivu.com/blog/2026/03/du-lich-ha-long-tiet-kiem-10-dia-diem-vui-choi-mien-phi-va-co-gia-re/",
    "https://mia.vn/cam-nang-du-lich/du-lich-lao-cai-12567",
    "https://pystravel.vn/tin/6526-kinh-nghiem-du-lich-thac-ban-gioc.html",
    "https://www.ivivu.com/blog/2024/12/cam-nang-du-lich-moc-chau-tu-a-den-z/",
    "https://www.ivivu.com/blog/2022/09/review-lang-son-2n1d-diem-den-moi-noi-trong-lang-du-lich/",
    "https://mia.vn/cam-nang-du-lich/goi-y-lich-trinh-yen-bai-nghia-lo-mu-cang-chai-3-ngay-tu-tuc-4350",
    "https://www.ivivu.com/blog/2026/06/cam-nang-du-lich-bien-do-son-hai-phong-tu-a-z/",
]


def crawl_article(url: str) -> dict:
    """
    Crawl một bài viết và trả về dict chứa metadata + content.

    Returns:
        {
            "url": str,
            "title": str,
            "date_crawled": str (ISO format),
            "content_markdown": str
        }
    """
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Chỉ loại bỏ những thẻ chắc chắn không chứa nội dung hiển thị trước khi chọn container —
    # KHÔNG decompose nav/header/footer/aside ở bước này: một số site bọc toàn bộ nội dung
    # bài viết bên trong <header>, decompose sớm sẽ xoá sạch nội dung.
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

    title = soup.title.get_text(strip=True) if soup.title else url

    # Chọn container có text dài nhất trong số article/section/div/main/header — không ưu
    # tiên mù quáng thẻ <article> vì một số trang dùng nó cho widget nhỏ thay vì nội dung chính.
    container, best_len = None, 0
    for c in soup.find_all(["article", "section", "div", "main", "header"]):
        length = len(c.get_text(strip=True))
        if length > best_len:
            container, best_len = c, length

    # Dọn nav/footer/aside/form lồng bên trong container đã chọn (menu, banner, form đăng ký...)
    if container is not None:
        for tag in container.find_all(["nav", "footer", "aside", "form"]):
            tag.decompose()

    text = container.get_text("\n", strip=True) if container else soup.get_text("\n", strip=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    content_markdown = "\n".join(lines)
    content_markdown = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", content_markdown)

    return {
        "url": url,
        "title": title,
        "date_crawled": datetime.now(timezone.utc).isoformat(),
        "content_markdown": content_markdown,
    }


def crawl_all():
    """Crawl toàn bộ bài viết trong ARTICLE_URLS."""
    setup_directory()

    for i, url in enumerate(ARTICLE_URLS, 1):
        print(f"[{i}/{len(ARTICLE_URLS)}] Crawling: {url}")
        article = crawl_article(url)

        filename = f"article_{i:02d}.json"
        filepath = DATA_DIR / filename
        filepath.write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  ✓ Saved: {filepath} ({len(article['content_markdown'])} chars)")


if __name__ == "__main__":
    if not ARTICLE_URLS:
        print("⚠ Hãy điền ARTICLE_URLS trước khi chạy!")
    else:
        crawl_all()
