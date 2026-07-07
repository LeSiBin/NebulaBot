import os
import re
import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as md

BASE_URL = "https://support.optisigns.com"
START_URL = f"{BASE_URL}/hc/en-us"

def slugify(text: str) -> str:
    """Chuyển đổi tiêu đề bài viết thành slug hợp lệ để đặt tên file."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text

def clean_markdown(html_element) -> str:
    """Chuyển đổi element HTML sang Markdown sạch, giữ lại heading, code blocks, links."""
    if not html_element:
        return ""
    
    # Chuyển đổi sang markdown
    markdown_text = md(
        str(html_element),
        heading_style="ATX",
        strip=['nav', 'footer', 'script', 'style', 'header', 'aside', 'form']
    )
    return markdown_text.strip()

def get_article_urls(max_urls=35) -> list:
    """Quét trang chủ hỗ trợ để thu thập danh sách URL của các bài viết."""
    print(f"🔍 Đang quét danh sách bài viết từ: {START_URL}")
    urls = set()
    
    with httpx.Client(follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"}) as client:
        try:
            response = client.get(START_URL, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Tìm tất cả các thẻ <a> chứa đường dẫn tới bài viết dạng /hc/en-us/articles/...
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]
                if "/hc/en-us/articles/" in href:
                    # Chuẩn hóa URL đầy đủ
                    full_url = href if href.startswith("http") else f"{BASE_URL}{href}"
                    # Loại bỏ phần tham số tìm kiếm nếu có (?biến=...)
                    full_url = full_url.split("?")[0]
                    urls.add(full_url)
                    if len(urls) >= max_urls:
                        break
        except Exception as e:
            print(f"❌ Lỗi khi lấy danh sách URL: {e}")
            
    return list(urls)

def fetch_and_convert_articles(output_dir="data", max_articles=35):
    """Truy cập từng URL bài viết, cào nội dung và lưu thành file .md."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    article_urls = get_article_urls(max_urls=max_articles)
    if not article_urls:
        print("❌ Không tìm thấy bài viết nào để cào dữ liệu.")
        return []

    print(f"📋 Đã tìm thấy {len(article_urls)} bài viết tiềm năng. Bắt đầu tải nội dung...")
    processed_articles = []

    with httpx.Client(follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"}) as client:
        for index, url in enumerate(article_urls, 1):
            try:
                print(f"🔄 [{index}/{len(article_urls)}] Đang cào dữ liệu: {url}")
                response = client.get(url, timeout=15)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Cấu trúc chuẩn của trang Zendesk: Tiêu đề nằm trong h1.article-title hoặc lớp tương đương
                title_element = soup.find("h1") or soup.find(class_="article-title")
                title = title_element.text.strip() if title_element else f"Untitled Article {index}"
                
                # Nội dung bài viết thường nằm trong class .article-body hoặc .article-content
                body_element = soup.find(class_="article-body") or soup.find(class_="article-content") or soup.find("article")
                
                if not body_element:
                    print(f"⚠️ Không tìm thấy phần thân bài viết cho URL: {url}, bỏ qua.")
                    continue

                slug = slugify(title)
                file_name = f"{slug}.md"
                file_path = os.path.join(output_dir, file_name)

                # Chuyển đổi nội dung sang Markdown
                markdown_content = clean_markdown(body_element)

                # Thêm URL gốc vào cuối bài viết phục vụ trích dẫn (Yêu cầu ở Bước 2)
                full_content = f"# {title}\n\n{markdown_content}\n\nArticle URL: {url}"

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(full_content)

                processed_articles.append({
                    "url": url,
                    "title": title,
                    "file_path": file_path
                })
                
            except Exception as e:
                print(f"❌ Lỗi khi xử lý bài viết {url}: {e}")
                continue

    print(f"✅ HOÀN THÀNH: Đã lưu thành công {len(processed_articles)} file Markdown vào thư mục '{output_dir}'.")
    return processed_articles

if __name__ == "__main__":
    fetch_and_convert_articles()