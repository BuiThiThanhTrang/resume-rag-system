# Resume Intelligence Platform

Resume Intelligence Platform is an end-to-end resume RAG system for extracting structured information from PDF resumes and searching candidates across multiple domains.

The project targets the assignment requirement: one RAG system for both:

- `BANKING`
- `INFORMATION-TECHNOLOGY`

The system now has two UI options:

- **Node.js frontend + FastAPI backend**: recommended for a cleaner product UI and easier screen/component management.
- **Streamlit app**: still available as a Python-only fallback/demo UI.

## What This Project Does

- Reads resume PDFs from `data/raw/BANKING` and `data/raw/INFORMATION-TECHNOLOGY`.
- Extracts text from PDFs with PyMuPDF.
- Falls back to OCR with Tesseract when a PDF page has too little embedded text.
- Extracts structured candidate profiles into JSON.
- Supports multiple extraction modes:
  - `rule_based`
  - `openai`
  - `langchain_openai`
- Builds a local TF-IDF retrieval index.
- Lets HR users search candidates across both domains.
- Shows candidate cards, match score, skills, extracted profile, and evidence.
- Provides analytics and local monitoring.
- Supports optional Phoenix tracing for LangChain/OpenAI calls.
- Includes evaluation scripts for extraction and RAG retrieval.

## Tech Stack

Backend:

- Python
- FastAPI
- Uvicorn
- PyMuPDF
- pytesseract
- Pydantic
- LangChain
- OpenAI SDK
- Phoenix/OpenInference/OpenTelemetry
- Custom TF-IDF retrieval store

Frontend:

- Node.js
- Native HTTP server
- Browser ES modules
- Vanilla JavaScript
- CSS

No frontend framework is required. There is no React/Vite build step.

## Project Structure

```text
resume-rag-system/
|-- api/
|   |-- __init__.py
|   `-- main.py
|-- app/
|   |-- __init__.py
|   `-- streamlit_app.py
|-- data/
|   |-- raw/
|   |   |-- BANKING/
|   |   `-- INFORMATION-TECHNOLOGY/
|   `-- Resume/
|       `-- Resume.csv
|-- evaluation/
|   |-- evaluate.py
|   |-- extract_eval.py
|   `-- ground_truth_sample.json
|-- frontend/
|   |-- package.json
|   |-- server.js
|   |-- public/
|   |   `-- index.html
|   `-- src/
|       |-- api/
|       |   `-- client.js
|       |-- components/
|       |   |-- CandidateCard.js
|       |   |-- DetailPanel.js
|       |   |-- Header.js
|       |   |-- MetricCard.js
|       |   |-- Sidebar.js
|       |   `-- Tabs.js
|       |-- screens/
|       |   |-- AnalyticsScreen.js
|       |   |-- CandidatesScreen.js
|       |   `-- SearchScreen.js
|       |-- utils/
|       |   `-- format.js
|       |-- main.js
|       |-- state.js
|       `-- styles.css
|-- prompts/
|   `-- extraction_prompt.txt
|-- services/
|   |-- monitoring.py
|   |-- pdf_service.py
|   |-- phoenix_tracing.py
|   |-- rag_service.py
|   `-- resume_extractor.py
|-- utils/
|   |-- env_loader.py
|   |-- file_utils.py
|   |-- find_scanned_pdfs.py
|   `-- text_utils.py
|-- vector_db/
|   `-- simple_store.py
|-- .env
|-- .gitignore
|-- config.py
|-- README.md
`-- requirements.txt
```

## Important Files

`api/main.py`

FastAPI backend used by the Node.js frontend.

Main endpoints:

- `GET /api/health`
- `GET /api/config`
- `POST /api/ingest`
- `POST /api/search`
- `GET /api/profiles`
- `GET /api/events`
- `DELETE /api/events`
- `GET /api/analytics`

`frontend/src/screens/SearchScreen.js`

Main search screen with candidate cards and candidate detail panel.

`frontend/src/screens/CandidatesScreen.js`

Table of extracted candidate profiles.

`frontend/src/screens/AnalyticsScreen.js`

Analytics, Phoenix status, and runtime events.

`services/rag_service.py`

Main RAG orchestration:

1. Read PDFs.
2. Extract text.
3. Extract structured profile.
4. Save JSON.
5. Chunk text.
6. Build retrieval index.
7. Search candidates.

`services/resume_extractor.py`

Extraction engines:

- rule-based
- OpenAI SDK
- LangChain + OpenAI

`services/pdf_service.py`

PDF text extraction and OCR fallback.

`vector_db/simple_store.py`

Local TF-IDF search index.

`services/monitoring.py`

Local monitoring logs.

`services/phoenix_tracing.py`

Optional Phoenix tracing setup.

## Current Dataset

The project currently contains:

| Path | Count |
| --- | ---: |
| `data/raw/BANKING` | 115 PDFs |
| `data/raw/INFORMATION-TECHNOLOGY` | 120 PDFs |

The file `data/Resume/Resume.csv` contains 2484 rows with:

- `ID`
- `Resume_str`
- `Resume_html`
- `Category`

The main pipeline uses the PDFs in `data/raw/...`.

## Prerequisites

Install these first:

- Python 3.10+
- Node.js 18+
- Git

Optional:

- Tesseract OCR, only needed if you have scanned PDFs.
- Phoenix, only needed for tracing.

Check Python:

```powershell
python --version
```

Check Node:

```powershell
node --version
npm --version
```

## 1. Activate Python Environment

Open PowerShell:

```powershell
cd D:\SideProject\resume-rag-system
```

Activate your existing virtual environment:

```powershell
.\resume_reader\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\resume_reader\Scripts\Activate.ps1
```

After activation, you should see:

```text
(resume_reader) PS D:\SideProject\resume-rag-system>
```

## 2. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

If you want to install only the core dependencies manually:

```powershell
pip install fastapi uvicorn streamlit pymupdf pytesseract pillow pandas pydantic python-dotenv langchain langchain-openai openai
```

Optional Phoenix dependencies:

```powershell
pip install arize-phoenix openinference-instrumentation-langchain openinference-instrumentation-openai opentelemetry-sdk opentelemetry-exporter-otlp
```

## 3. Install Node Dependencies

The frontend uses native Node.js and browser ES modules, so there are currently no external npm packages.

Still, run this once to verify npm can read the project:

```powershell
cd D:\SideProject\resume-rag-system\frontend
npm install
```

This should be quick because `package.json` has no external dependencies.

## 4. Configure `.env`

Open:

```text
D:\SideProject\resume-rag-system\.env
```

Example:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
PHOENIX_ENABLED=false
PHOENIX_PROJECT_NAME=resume-rag-system
PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006/v1/traces
PHOENIX_UI_URL=http://localhost:6006
```

The app automatically loads `.env`.

For offline rule-based mode, you do not need a real OpenAI key.

For OpenAI or LangChain + OpenAI mode, replace:

```env
OPENAI_API_KEY=your_api_key_here
```

with your real key.

## 5. Run The System With Node.js Frontend

This is the recommended way.

### Terminal 1: Start Backend API

```powershell
cd D:\SideProject\resume-rag-system
.\resume_reader\Scripts\Activate.ps1
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Backend URL:

```text
http://localhost:8000
```

API docs:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/api/health
```

### Terminal 2: Start Frontend

```powershell
cd D:\SideProject\resume-rag-system\frontend
npm start
```

Frontend URL:

```text
http://localhost:5173
```

## 6. Use The App

In the frontend:

1. Select domains:
   - Banking
   - Information Technology
2. Select extraction mode:
   - `Rule-based`
   - `OpenAI SDK`
   - `LangChain + OpenAI`
3. Set `Files per domain`.
4. Click `Build / rebuild index`.
5. Search candidates.

Example queries:

```text
Find IT candidates with Python, SQL, and data analysis experience.
```

```text
Find banking candidates with credit risk or loan experience.
```

```text
Find candidates with customer service and finance background.
```

## 7. Run Streamlit App Instead

Streamlit is still available if you want a Python-only UI:

```powershell
cd D:\SideProject\resume-rag-system
.\resume_reader\Scripts\Activate.ps1
streamlit run app/streamlit_app.py
```

Open:

```text
http://localhost:8501
```

## 8. Enable Phoenix Monitoring

By default, Phoenix is disabled:

```env
PHOENIX_ENABLED=false
```

To enable Phoenix:

1. Install dependencies:

```powershell
pip install arize-phoenix openinference-instrumentation-langchain openinference-instrumentation-openai opentelemetry-sdk opentelemetry-exporter-otlp
```

2. Start Phoenix in a separate terminal:

```powershell
cd D:\SideProject\resume-rag-system
.\resume_reader\Scripts\Activate.ps1
phoenix serve
```

3. Open:

```text
http://localhost:6006
```

4. Edit `.env`:

```env
PHOENIX_ENABLED=true
PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006/v1/traces
PHOENIX_UI_URL=http://localhost:6006
```

5. Restart the backend:

```powershell
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Phoenix is optional. Local monitoring still works without it.

## 9. Run Extraction Evaluation

Rule-based:

```powershell
python evaluation/extract_eval.py --max-files-per-domain 10 --extraction-mode rule_based
```

OpenAI:

```powershell
python evaluation/extract_eval.py --max-files-per-domain 10 --extraction-mode openai
```

LangChain + OpenAI:

```powershell
python evaluation/extract_eval.py --max-files-per-domain 10 --extraction-mode langchain_openai
```

Outputs:

```text
runtime_outputs/evaluation/extract_eval_report.json
runtime_outputs/evaluation/extract_eval_metrics.csv
```

With ground truth:

```powershell
python evaluation/extract_eval.py --max-files-per-domain 10 --extraction-mode rule_based --ground-truth evaluation/ground_truth_sample.json
```

## 10. Run RAG Evaluation

Build the index once, then:

```powershell
python evaluation/evaluate.py --top-k 5
```

This prints:

- query
- latency
- retrieved resume evidence
- source file/domain

## 11. Find Scanned PDFs That Need OCR

```powershell
python utils/find_scanned_pdfs.py
```

Increase threshold:

```powershell
python utils/find_scanned_pdfs.py --min-text-chars 120
```

## Output Files

Extracted candidate JSON:

```text
extracted_json/<DOMAIN>/<PDF_ID>.json
```

Fallback output location:

```text
runtime_outputs/extracted_json/<DOMAIN>/<PDF_ID>.json
```

Vector index:

```text
vector_db/store/tfidf_index.pkl
```

Monitoring logs:

```text
runtime_outputs/monitoring/events.jsonl
```

Evaluation reports:

```text
runtime_outputs/evaluation/
```

## Common Issues

### PowerShell cannot activate virtual environment

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\resume_reader\Scripts\Activate.ps1
```

### Frontend says API is not ready

Make sure backend is running:

```powershell
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

```text
http://localhost:8000/api/health
```

You should see:

```json
{"status":"ok"}
```

### Phoenix connection refused

Either keep Phoenix disabled:

```env
PHOENIX_ENABLED=false
```

or start Phoenix:

```powershell
phoenix serve
```

### OpenAI mode falls back to rule-based

Check `.env`:

```env
OPENAI_API_KEY=your_real_api_key
OPENAI_MODEL=gpt-4o-mini
```

Restart backend after editing `.env`.

### Node command fails

Check Node installation:

```powershell
node --version
npm --version
```

If missing, install Node.js 18+ from:

```text
https://nodejs.org/
```

## Recommended Demo Flow

1. Start FastAPI backend.
2. Start Node.js frontend.
3. Open `http://localhost:5173`.
4. Select both domains.
5. Choose `Rule-based`.
6. Build index with `10` files per domain.
7. Search candidates.
8. Inspect candidate detail.
9. Open Analytics.
10. Optionally enable Phoenix.
11. Optionally test `LangChain + OpenAI`.

## Limitations

- Retrieval currently uses TF-IDF, not dense embeddings.
- Rule-based extraction is a baseline.
- LLM modes require OpenAI API access.
- Phoenix requires a separate running Phoenix server.
- `Resume.csv` is useful for category-level evaluation, not full entity-level extraction ground truth.

## Possible Improvements

- Replace TF-IDF with FAISS/Chroma and sentence-transformer embeddings.
- Add labeled ground truth for 50-100 resumes.
- Add entity-level precision/recall/F1.
- Add export buttons for candidate JSON and evaluation CSV.
- Add Docker Compose for backend, frontend, and Phoenix.

## Submission Notes

Recommended email title:

```text
Test Assignment Submission - YOUR NAME - AI Intern
```

Submit:

- GitHub repository link.
- Demo link or screenshots/video.
- README as the technical report.
