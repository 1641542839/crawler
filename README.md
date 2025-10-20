# Web Crawler

A Python-based web crawler that recursively crawls websites while respecting `robots.txt` and saving content with metadata.

## Features

- **Recursive Crawling**: Crawls websites up to a configurable depth
- **Respects robots.txt**: Automatically checks and respects robots.txt rules for each domain
- **Smart URL Filtering**: Only follows links on the same hostname and within the seed path prefix
- **Retry Logic**: Automatically retries transient errors up to 3 times with exponential backoff
- **Rate Limiting**: Random delays between requests to be polite to servers
- **File Downloads**: Automatically downloads linked PDF, DOC, and DOCX files
- **Metadata Tracking**: Logs detailed metadata for each crawled page in JSON Lines format
- **Progress Bar**: Visual progress tracking (when tqdm is installed)

## Installation

### Requirements

- Python 3.6+
- Required packages:
  ```bash
  pip install -r requirements.txt
  ```

  Or install manually:
  ```bash
  pip install requests beautifulsoup4 tqdm
  ```

## Usage

### Basic Usage

1. Create a `seeds.txt` file with URLs to crawl (one per line):
   ```
   https://example.com/
   https://www.python.org/doc/
   ```

2. Run the crawler:
   ```bash
   python crawler.py
   ```

### Command-Line Options

```bash
python crawler.py [OPTIONS]
```

#### Available Options

- `--seeds PATH`: Path to seeds file (default: `seeds.txt`)
  - One URL per line
  - Lines starting with `#` are treated as comments

- `--depth N`: Maximum crawl depth from each seed (default: `3`)
  - Depth 0: Only crawl seed URLs
  - Depth 1: Crawl seeds + direct links
  - Depth 2: Crawl seeds + links + links from links, etc.

- `--delay-min SECONDS`: Minimum delay between requests (default: `1.0`)

- `--delay-max SECONDS`: Maximum delay between requests (default: `3.0`)
  - Actual delay is randomly chosen between min and max

- `--max-pages N`: Maximum number of pages to crawl (default: `0` for unlimited)

- `--user-agent STRING`: User agent string for requests (default: `Mozilla/5.0 (compatible; CustomCrawler/1.0)`)

- `--verbose`: Enable verbose logging to see detailed progress

### Examples

1. **Crawl with default settings:**
   ```bash
   python crawler.py
   ```

2. **Crawl with custom depth and delay:**
   ```bash
   python crawler.py --depth 5 --delay-min 2.0 --delay-max 5.0
   ```

3. **Crawl with a limit on pages:**
   ```bash
   python crawler.py --max-pages 100
   ```

4. **Verbose output:**
   ```bash
   python crawler.py --verbose
   ```

5. **Use custom seeds file:**
   ```bash
   python crawler.py --seeds my_urls.txt --depth 2
   ```

## Output Structure

The crawler creates the following directory structure:

```
data/
├── raw/
│   ├── YYYYMMDD/
│   │   ├── hostname_sha1hash.html
│   │   └── ...
│   └── index.jsonl
└── raw_files/
    ├── sha1hash.pdf
    ├── sha1hash.doc
    └── ...
```

### Output Files

1. **HTML Files**: `data/raw/YYYYMMDD/<hostname>_<sha1>.html`
   - Raw HTML content saved with date-based organization
   - Filename includes hostname and SHA1 hash of URL

2. **Downloaded Files**: `data/raw_files/<sha1>.<ext>`
   - PDF, DOC, DOCX files linked from crawled pages
   - Filename is SHA1 hash of URL with original extension

3. **Metadata Index**: `data/raw/index.jsonl`
   - JSON Lines format (one JSON object per line)
   - Each line contains metadata for a crawled page:
     ```json
     {
       "url": "https://example.com/page",
       "status_code": 200,
       "content_type": "text/html; charset=utf-8",
       "saved_path": "data/raw/20231020/example.com_abc123.html",
       "crawl_date": "2023-10-20T14:30:00.123456",
       "depth": 1,
       "parent_url": "https://example.com/",
       "content_length": 12345
     }
     ```

## How It Works

1. **Seed Reading**: Reads URLs from seeds.txt, ignoring comments and empty lines

2. **URL Queue**: Maintains a queue of URLs to visit with their depth level

3. **Robots.txt Check**: Before fetching any URL, checks if it's allowed by robots.txt

4. **Fetch with Retry**: Fetches content with up to 3 retry attempts for transient errors

5. **Link Extraction**: Parses HTML to find all links using BeautifulSoup

6. **Link Filtering**: Only follows links that:
   - Are on the same hostname as the seed
   - Have paths starting with the seed's path prefix
   - Haven't been visited yet

7. **Content Saving**: Saves HTML and files with descriptive filenames and logs metadata

8. **Progress Tracking**: Updates progress bar or logs progress in verbose mode

## Crawling Rules

### Same Hostname Rule
Only URLs with the same hostname as the seed are followed.

**Example:**
- Seed: `https://example.com/docs/`
- ✓ Allowed: `https://example.com/docs/page1`
- ✗ Blocked: `https://other.com/page`
- ✗ Blocked: `https://subdomain.example.com/page`

### Path Prefix Rule
Only URLs whose path starts with the seed's path are followed.

**Example:**
- Seed: `https://example.com/docs/`
- ✓ Allowed: `https://example.com/docs/guide/`
- ✓ Allowed: `https://example.com/docs/api`
- ✗ Blocked: `https://example.com/blog/`
- ✗ Blocked: `https://example.com/about`

### Robots.txt
The crawler respects robots.txt for each domain. If a URL is disallowed, it will be skipped.

## Notes

- The crawler is designed to be polite and respectful to web servers
- Always check a website's terms of service before crawling
- Use appropriate delays to avoid overloading servers
- The crawler does not execute JavaScript (only parses static HTML)
- Duplicate URLs (same URL visited twice) are automatically skipped

## Troubleshooting

### "Required library not found"
Install the required packages:
```bash
pip install requests beautifulsoup4
```

### "Seeds file not found"
Make sure `seeds.txt` exists or specify a different file with `--seeds`

### Slow crawling
- Adjust `--delay-min` and `--delay-max` to smaller values (but be respectful!)
- Note that robots.txt rules and retry logic may also affect speed

### "Disallowed by robots.txt"
The website's robots.txt file prohibits crawling that URL. This is respected by design.
# Local-First RAG Pipeline

A local-first Retrieval-Augmented Generation (RAG) pipeline for processing and indexing documents.

## Directory Layout

The project uses the following directory structure:

```
./data/
├── raw/              # Raw data files
├── raw_files/        # Original uploaded files
├── parsed/           # Parsed document content
├── tables/           # Extracted tables from documents
├── chunks.jsonl      # Chunked text data for indexing
└── faiss_index/      # FAISS vector index
```

## Quick Start

### 1. Create a virtual environment

```bash
python -m venv venv
```

### 2. Activate the virtual environment

**On Linux/Mac:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create data directories

```bash
mkdir -p data/raw data/raw_files data/parsed data/tables data/faiss_index
```

## Dependencies

This project requires the following Python packages:
- `requests` - HTTP library for web requests
- `beautifulsoup4` - HTML/XML parsing
- `markdownify` - Convert HTML to Markdown
- `pdfplumber` - PDF text extraction
- `camelot-py[cv]` - PDF table extraction
- `python-docx` - DOCX file handling
- `pytesseract` - OCR capabilities
- `pandas` - Data manipulation
- `sentence-transformers` - Text embeddings
- `faiss-cpu` - Vector similarity search
- `fastapi` - Web framework
- `uvicorn[standard]` - ASGI server
- `python-dotenv` - Environment variable management
- `tqdm` - Progress bars
