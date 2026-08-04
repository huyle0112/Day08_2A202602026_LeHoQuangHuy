"""
Task 1 — Thu thập "cẩm nang du lịch" chính cho chủ đề Trợ Lý Hướng Dẫn Viên Du Lịch.

Chủ đề: Trợ Lý Hướng Dẫn Viên Du Lịch Thông Minh — phạm vi 10 tỉnh/thành miền Bắc Việt Nam
(xem SUGGESTED_TOPICS.md, mục 5): Hà Nội, Hà Giang, Ninh Bình, Quảng Ninh, Lào Cai,
Cao Bằng, Sơn La, Lạng Sơn, Yên Bái, Hải Phòng.

Nguồn: mỗi tỉnh 1 bài "cẩm nang du lịch từ A-Z" từ các trang cẩm nang du lịch uy tín
(vnexpress.net, mia.vn, ivivu.com, vietthangtravel.com, blog.vexere.com, pystravel.vn,
catbaexpress.com) — đóng vai trò văn bản tham khảo nền tảng/toàn diện nhất cho mỗi tỉnh,
tương đương vai trò policy document trong đề bài gốc.

Cách làm: các trang này là HTML server-rendered (không cần JS/browser), nên ta:
    1. Tải HTML bằng requests
    2. Trích xuất nội dung bài viết bằng BeautifulSoup (bỏ script/style/nav/footer)
    3. Convert nội dung text sang PDF bằng fpdf2 (dùng font Unicode để giữ dấu tiếng Việt/ký
       tự đặc biệt nếu có)
    4. Lưu vào data/landing/legal/
"""

import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from fpdf import FPDF

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RAGLabBot/1.0"}

# Font Unicode có sẵn trên Windows, dùng để fpdf2 render được ký tự ngoài Latin-1 cơ bản.
UNICODE_FONT_PATH = Path("C:/Windows/Fonts/arial.ttf")

# Cẩm nang du lịch từ A-Z cho 10 tỉnh/thành miền Bắc (1 bài / tỉnh)
LEGAL_DOCS = [
    {
        "url": "https://vnexpress.net/cam-nang-du-lich-ha-noi-4459188.html",
        "filename": "cam-nang-du-lich-ha-noi.pdf",
    },
    {
        "url": "https://pystravel.vn/tin/5652-cam-nang-du-lich-ha-giang.html",
        "filename": "cam-nang-du-lich-ha-giang.pdf",
    },
    {
        "url": "https://blog.vexere.com/du-lich-ninh-binh/",
        "filename": "cam-nang-du-lich-ninh-binh.pdf",
    },
    {
        "url": "https://mia.vn/cam-nang-du-lich/du-lich-quang-ninh-12413",
        "filename": "cam-nang-du-lich-quang-ninh.pdf",
    },
    {
        "url": "https://mia.vn/cam-nang-du-lich/du-lich-sapa-12275",
        "filename": "cam-nang-du-lich-lao-cai-sapa.pdf",
    },
    {
        "url": "https://vietthangtravel.com/cam-nang-du-lich-cao-bang-2026",
        "filename": "cam-nang-du-lich-cao-bang.pdf",
    },
    {
        "url": "https://mia.vn/cam-nang-du-lich/du-lich-moc-chau-12033",
        "filename": "cam-nang-du-lich-son-la-moc-chau.pdf",
    },
    {
        "url": "https://mia.vn/cam-nang-du-lich/du-lich-lang-son-12496",
        "filename": "cam-nang-du-lich-lang-son.pdf",
    },
    {
        "url": "https://mia.vn/cam-nang-du-lich/du-lich-mu-cang-chai-20639",
        "filename": "cam-nang-du-lich-yen-bai-mu-cang-chai.pdf",
    },
    {
        "url": "https://catbaexpress.com/kinh-nghiem-du-lich-cat-ba.html",
        "filename": "cam-nang-du-lich-hai-phong-cat-ba.pdf",
    },
]


def setup_directory():
    """Tạo thư mục data/landing/legal/ nếu chưa có."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Thư mục đã sẵn sàng: {DATA_DIR}")


def extract_article_text(url: str) -> tuple[str, str]:
    """Tải trang và trích xuất (title, plain_text) từ nội dung bài viết chính."""
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Chỉ loại bỏ những thẻ chắc chắn không chứa nội dung hiển thị trước khi chọn container —
    # KHÔNG decompose nav/header/footer/aside ở bước này: một số site (vd. catbaexpress.com)
    # bọc toàn bộ nội dung bài viết bên trong <header>, decompose sớm sẽ xoá sạch nội dung.
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

    title = soup.title.get_text(strip=True) if soup.title else url
    # Chọn container có text dài nhất trong số article/section/div/main/header — không ưu
    # tiên mù quáng thẻ <article> vì một số trang dùng nó cho widget nhỏ (vd. "related posts")
    # thay vì nội dung chính, khiến extract ra gần như rỗng.
    candidates = soup.find_all(["article", "section", "div", "main", "header"])
    container, best_len = None, 0
    for c in candidates:
        length = len(c.get_text(strip=True))
        if length > best_len:
            container, best_len = c, length

    # Dọn nav/footer/aside/form lồng bên trong container đã chọn (menu, banner, form đăng ký...)
    if container is not None:
        for tag in container.find_all(["nav", "footer", "aside", "form"]):
            tag.decompose()

    text = container.get_text("\n", strip=True) if container else soup.get_text("\n", strip=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return title, "\n".join(lines)


def save_as_pdf(title: str, text: str, filepath: Path):
    """Ghi title + text ra file PDF, dùng font Unicode để hỗ trợ ký tự đặc biệt."""
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Arial", "", str(UNICODE_FONT_PATH))
    pdf.set_font("Arial", size=16)
    pdf.multi_cell(0, 10, title)
    pdf.ln(4)
    pdf.set_font("Arial", size=11)
    # fpdf2 không tự xử lý control char lạ -> loại bỏ ký tự không in được
    clean_text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    pdf.multi_cell(0, 6, clean_text)
    pdf.output(str(filepath))


def download_file(url: str, filename: str):
    """Tải 1 bài patch note và lưu thành PDF trong DATA_DIR."""
    print(f"Downloading: {url}")
    title, text = extract_article_text(url)
    filepath = DATA_DIR / filename
    save_as_pdf(title, text, filepath)
    print(f"  ✓ Đã tải: {filepath} ({len(text)} chars)")


def collect_all():
    """Tải toàn bộ văn bản trong LEGAL_DOCS."""
    setup_directory()
    for doc in LEGAL_DOCS:
        download_file(doc["url"], doc["filename"])


if __name__ == "__main__":
    collect_all()
