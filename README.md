Nebula Bot Assistant (OptiBot Mini-Clone)
A production-ready daily data synchronization pipeline and AI Assistant built with Python and Google Gemini. This project automates the ingestion of messy customer support content, indexes it into a knowledge base, and provides factual, cited answers.

🚀 Setup & Installation
1. Prerequisites
Ensure you have the following installed on your local machine:

Python 3.11+

2. Environment Configuration
Create a .env file in the root directory of the project and add your Google Gemini API key:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

(Note: A .env.sample file is provided in the repository for reference.)

3. Execution & Deployment
To run the pipeline and synchronize data locally:

```bash
# Install required dependencies
pip install -r requirements.txt

# Execute the daily data synchronization job
python main.py
```

🧠 Technical Architectures & Strategies
1. Scraping Strategy
Since direct public API endpoints might be restricted or structurally modified, the pipeline utilizes a robust HTML parsing strategy using BeautifulSoup4 and httpx. It scans the main Help Center layout, safely extracts individual article links, cleans unwanted layout nodes (navigation bars, footers, scripts), and normalizes the core article body into clean Markdown.

2. Chunking & Knowledge Base Strategy
Chunking Strategy: Content is divided into fixed-size chunks of 1000 characters with a 200-character overlap. The overlap ensures semantic continuity across chunk boundaries, preventing critical instructional steps from being split and losing context.

Vector Store Injection: The pipeline utilizes Google Gemini's advanced semantic embedding infrastructure (text-embedding-004). It uploads document deltas directly via API, ensuring the automated chatbot assistant retains strict alignment with the latest documentation.

3. Smart Delta Detection (Incremental Updates)
To optimize network bandwidth and minimize API rate limit consumption, the pipeline implements an MD5 hashing mechanism:

Each scraped article's content is hashed (hashlib.md5).

Hashes are compared against a local tracking registry (data_cache.json).

Added: New articles are immediately uploaded.

Updated: Modifications trigger a re-upload to refresh the vector store.

Skipped: Unchanged articles are completely bypassed, yielding high efficiency.

📊 Job Statistics (Sample Logs)
When running sequentially, the pipeline outputs structured reports detailing execution counts in the terminal:

```text
📊 BÁO CÁO KẾT QUẢ TÁC VỤ (JOB LOGS):
➕ Số bài viết THÊM MỚI (Added): 0
🔄 Số bài viết CẬP NHẬT (Updated): 0
⏭️ Số bài viết BỎ QUA (Skipped): 21
```

🔗 Project Deliverables & Artifacts
Execution Logs: (Please refer to the attached terminal screenshot showing successful local execution logs with MD5 delta detection)

Assistant Screenshot: (Please check the screenshot attached in the submission folder showing the Assistant answering with proper citations)