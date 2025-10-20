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
