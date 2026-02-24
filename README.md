# IITM Discourse Community — Data Story

A data scraping, analysis, and storytelling project built around the **IIT Madras Online Degree Programme Discourse Forum**. It fetches paginated user-directory data from the forum API, combines it into a single dataset, runs a full statistical analysis, and produces a beautiful HTML data story with charts and narrative.

---

## Project Structure

```
15_feb/
├── main.py          # Discourse API scraper (fetches user directory, page by page)
├── combine.py       # Merges all page_*.json files into data/combined.json
├── analyze.py       # Full analysis: stats, segmentation, 7 charts, summary JSON
├── datastory.html   # Self-contained HTML data story (open in browser)
├── data/
│   ├── page_1.json … page_10.json   # Raw paginated API responses
│   └── combined.json                # Merged dataset (500 users)
└── output/
    ├── trust_level_dist.png
    ├── engagement_segments.png
    ├── correlation_heatmap.png
    ├── post_distribution.png
    ├── time_vs_likes.png
    ├── top15_power_users.png
    ├── days_vs_posts.png
    └── summary.json                 # Structured stats used by the data story
```

---

## Workflow

### 1. Scrape
`main.py` hits the Discourse `/directory_items.json` endpoint with authenticated cookies, iterating through pages and saving each response as `data/page_N.json`.

### 2. Combine
```bash
python3 combine.py
```
Merges all page JSON files into `data/combined.json` — a single list of 500 user objects.

### 3. Analyse
```bash
python3 analyze.py
```
- Flattens nested JSON into a pandas DataFrame  
- Derives an **engagement index** (composite Z-score: posts + likes + days + solutions)  
- Segments users into **Power Users / Contributors / Silent Readers / Lurkers**  
- Computes a full correlation matrix across 7 engagement metrics  
- Outputs 7 charts to `output/` and a `summary.json`

### 4. View the Data Story
```bash
python3 -m http.server 7891
# Open: http://localhost:7891/datastory.html
```

---

## Key Findings (500 Users · Feb 2026)

| Metric | Value |
|---|---|
| Total posts created | 22,059 |
| Total reading time | 8,128 hours |
| Total solutions shared | 1,502 |
| Total likes given | 17,752 |
| Power Users (top 5%) | 25 users |
| Contributors | 399 (79.8%) |
| Lurkers | 64 (12.8%) |
| Posts ↔ Likes correlation | **r = 0.96** |
| Top contributor | Sayan Ghosh — 2,835 posts, 577 solutions |

---

## Dependencies

```
pandas
matplotlib
seaborn
numpy
requests
```

Install into your venv:
```bash
pip install pandas matplotlib seaborn numpy requests
```

---

## Context

This project was built as part of a **TDS (Tools in Data Science) live session** at IITM (February 2026).  
The goal was to demonstrate a full end-to-end data pipeline:  
**API scraping → data wrangling → statistical analysis → data storytelling**.
