# AI Workshop Streamlit Dashboard

Interactive dashboard for the fictional AI workshop inquiry dataset.

## What it does

The app uses **Streamlit, pandas, and matplotlib** to:

1. Answer all six questions from the workbook's **Start here** sheet.
2. Provide an executive summary with the main funnel KPIs.
3. Show channel performance, including inquiry volume, attendees, attendance rate, and response time.
4. Show the most requested workshop topics.
5. Show the six-week inquiry/registration/attendance trend.
6. Provide an operational next-step report and a five-slide presentation outline.
7. Provide interactive filters for week, discovery channel, and main interest.
8. Show data-quality checks and the cleaned raw data.

## Files

```text
ai_workshop_dashboard/
├── app.py
├── requirements.txt
├── README.md
└── AI_Workshop_Example_Data.xlsx   # place the supplied workbook here
```

## Installation

Python 3.10+ is recommended.

```bash
python -m venv .venv
```

Activate the environment:

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

Put `AI_Workshop_Example_Data.xlsx` in the same directory as `app.py`, then run:

```bash
streamlit run app.py
```

The app also has an Excel uploader in the sidebar, so the workbook does not have to be stored beside the app when uploading through the UI.

## Workbook expectations

The app expects an Excel workbook containing an `Inquiries` sheet with the same structure as the supplied file:

- Inquiry ID
- Inquiry date
- Week
- City
- Discovery channel
- Main interest
- Response hours
- Registered
- Attended
- Satisfaction /5

The first two rows of the `Inquiries` sheet are treated as title/metadata rows, and row 3 contains the column headers.

## Main metrics

The supplied dataset contains:

- 300 inquiries
- 176 registered
- 130 attended
- 4.2/5 average satisfaction among attendees
- 73.9% inquiry-to-attendance rate

**Important:** the workbook defines inquiry-to-attendance rate as attendees divided by inquiries, not attendees divided by registrations.

## Dashboard pages

### 1. Answers & Executive Summary

Answers the six questions from the workbook directly:

- Which channel brought the most inquiries?
- Which channel brought the most attendees?
- What topic is most requested?
- Does reply speed differ by channel?
- How did inquiries change over six weeks?
- What should the team do next?

It also includes the requested one-page action report and five-slide presentation outline.

### 2. Interactive Dashboard

Use the sidebar filters to explore:

- Week
- Discovery channel
- Main interest

Charts are generated with matplotlib.

### 3. Data & Methodology

Shows:

- metric definitions
- data-quality checks
- cleaned raw data

## Notes

This is fictional teaching data. The dashboard intentionally avoids causal claims. For example, different response times by channel do **not** prove that response time caused different registration or attendance outcomes.
