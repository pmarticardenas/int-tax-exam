# International Taxation — Exam Practice

Streamlit app for practising past International Taxation exam questions.

## Contents

- `app.py` — Streamlit application
- `question_bank.json` — 156 questions from 5 past exams (2017, 2018, 2019, 2024, 2025)
- `requirements.txt` — runtime dependencies (only streamlit)
- `progress.sqlite3` — auto-generated, stores your progress locally

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## Deploy on Streamlit Community Cloud

1. Push this folder to a GitHub repo
2. Open https://share.streamlit.io/
3. Select the repo, branch `main`, entrypoint `app.py`
4. Deploy — you get a URL you can open from your phone

## Features

- **Dashboard** with per-topic progress bars
- **Quiz mode**: practice all questions, unseen only, or failed only
- **Instant feedback** with colour-coded options and full explanation
- **Bookmarks** to flag questions for later review
- **Session resume** — sessions persist through reloads
- **Browser** — filter all questions by topic, year, status
- **Statistics** — progress by topic and by year

## Question bank

| Year | Questions |
|------|-----------|
| 2017 | 30 |
| 2018 | 30 |
| 2019 | 30 |
| 2024 | 30 |
| 2025 | 36 |
| **Total** | **156** |

Topics covered: OECD Guidelines, PO & SO Principles, Double Taxation Concepts,
Double Tax Conventions, PE, Transfer Pricing, Methods to Avoid DT,
BEPS & Anti-Avoidance, EU Directives, VAT & Indirect Taxation,
Tax Residency, Tax Fundamentals, Tax Calculations.
