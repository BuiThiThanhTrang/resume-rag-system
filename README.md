# Resume RAG System

This project implements the AI Team intern assignment: one RAG system that can search and extract structured information from BANKING and INFORMATION-TECHNOLOGY resumes.

## Features

- Reads text-based PDFs with PyMuPDF.
- Falls back to OCR for scanned pages when Tesseract is available.
- Extracts structured candidate JSON into `extracted_json/`. If that folder is not writable on Windows, the app automatically uses `runtime_outputs/extracted_json/`.
- Builds a local TF-IDF retrieval index for HR queries across both domains.
- Provides a Streamlit UI for indexing, querying, and reviewing extracted profiles.
- Supports selectable extraction modes: rule-based, OpenAI SDK, and LangChain + OpenAI.
- Uses LangChain runnables for the RAG query path.
- Logs runtime monitoring events for extraction and RAG queries, with optional Phoenix/OpenInference tracing.
- Includes a lightweight retrieval evaluation script.

## Folder Mapping

- `data/raw/BANKING` and `data/raw/INFORMATION-TECHNOLOGY`: required resume PDFs.
- `extracted_json/` or `runtime_outputs/extracted_json/`: generated structured candidate profiles.
- `services/pdf_service.py`: PDF and OCR text extraction.
- `services/resume_extractor.py`: JSON profile extraction. It works with rules by default and can use OpenAI when `OPENAI_API_KEY` is set.
- `services/rag_service.py`: ingestion and query workflow.
- `services/monitoring.py`: runtime monitoring for speed, CPU time, memory, errors, selected framework, and extraction status.
- `services/phoenix_tracing.py`: optional Phoenix tracing setup for LangChain and OpenAI calls.
- `vector_db/simple_store.py`: local searchable index.
- `app/streamlit_app.py`: Streamlit product demo.
- `evaluation/evaluate.py`: simple latency and retrieval sanity check.

## Setup

Activate the existing virtual environment:

```powershell
.\resume_reader\Scripts\Activate.ps1
```

Install dependencies if needed:

```powershell
pip install -r requirements.txt
```

Optional LLM extraction:

```powershell
$env:OPENAI_API_KEY="your_api_key"
$env:OPENAI_MODEL="gpt-4o-mini"
```

Optional Phoenix tracing:

```powershell
pip install arize-phoenix openinference-instrumentation-langchain openinference-instrumentation-openai opentelemetry-sdk opentelemetry-exporter-otlp
phoenix serve
```

In another terminal:

```powershell
$env:PHOENIX_PROJECT_NAME="resume-rag-system"
$env:PHOENIX_COLLECTOR_ENDPOINT="http://localhost:6006/v1/traces"
streamlit run app/streamlit_app.py
```

Open Phoenix at `http://localhost:6006`.

## Run The App

```powershell
streamlit run app/streamlit_app.py
```

Then open the local URL shown by Streamlit.

In the sidebar:

1. Select `BANKING` and `INFORMATION-TECHNOLOGY`.
2. Choose an extraction mode.
3. Choose a small number first, for example 20 files per domain.
4. Click `Build / rebuild index`.
5. Ask HR-style questions in the `HR Query` tab.

Extraction modes:

- `Rule-based (offline)`: no API key, fastest, deterministic baseline.
- `OpenAI SDK`: calls OpenAI directly for structured JSON extraction.
- `LangChain + OpenAI`: runs extraction through a LangChain prompt/LLM/parser chain.

Monitoring:

- Open the `Monitoring` tab in the app to inspect extraction/query events.
- Raw logs are stored in `runtime_outputs/monitoring/events.jsonl`.

Example queries:

- `Find IT candidates with Python, SQL, and data analysis experience.`
- `Find banking candidates with credit risk or loan experience.`
- `Which candidates have customer service and finance background?`

## Run Evaluation

Build the index once from the app, then run:

```powershell
python evaluation/evaluate.py --top-k 5
```

The script reports retrieval evidence and latency for sample queries. For a stronger report, manually review the top results and record whether each retrieved resume is relevant.

## Run Extraction Evaluation

Evaluate PDF extraction speed, CPU time, peak memory, and extraction quality:

```powershell
python evaluation/extract_eval.py --max-files-per-domain 10 --extraction-mode rule_based
```

Outputs are written to:

- `runtime_outputs/evaluation/extract_eval_report.json`
- `runtime_outputs/evaluation/extract_eval_metrics.csv`

If you have manually labeled ground truth, pass it as JSON or CSV:

```powershell
python evaluation/extract_eval.py --max-files-per-domain 10 --ground-truth evaluation/ground_truth_sample.json
```

Without ground truth, the script reports `proxy_accuracy`, based on whether key fields such as candidate name, email, phone, skills, summary, and extracted text are present.

## Find Scanned PDFs

Print PDF files that likely need OCR:

```powershell
python utils/find_scanned_pdfs.py
```

Adjust the threshold if needed:

```powershell
python utils/find_scanned_pdfs.py --min-text-chars 120
```

## Submission Notes

Recommended email title:

`Test Assignment Submission - YOUR NAME - AI Intern`

Submit:

- GitHub repository link.
- Demo link or screenshots/video.
- README as the short technical report.
