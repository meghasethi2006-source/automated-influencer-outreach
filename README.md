# Automated Micro-Influencer Outreach System

An AI-powered workflow for discovering, filtering, enriching, and managing outreach to micro-influencers in the Beauty & Skincare niche.

## Overview

This project automates the early stages of influencer outreach:

**Discovery → Filtering → Enrichment → Contact Extraction → AI Personalization → Validation → Outreach Tracking**

The current prototype uses YouTube as the discovery platform and focuses on Beauty & Skincare creators.

The system is designed as a modular pipeline so that each stage can be executed independently and extended to larger datasets or additional platforms.

## Features

- Discover influencers using the YouTube Data API
- Collect channel-level creator information
- Filter creators by subscriber count
- Calculate estimated engagement from recent videos
- Extract recent content titles
- Detect content themes
- Extract publicly available contact emails
- Store influencer and outreach information in SQLite
- Generate personalized email and Instagram DM content using Gemini
- Validate generated message word counts
- Track outreach status
- Prevent duplicate database entries
- Export structured CSV datasets
- Handle unavailable contact information without guessing
- Support manual/simulated Instagram outreach
- Continue the pipeline when external AI services are unavailable

## Technology Stack

- Python
- Pandas
- YouTube Data API v3
- Google Gemini API
- SQLite
- Regular Expressions
- python-dotenv
- CSV

## Project Structure

```text
automated-influencer-outreach/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── src/
│   ├── database.py
│   ├── discovery.py
│   ├── filtering.py
│   ├── enrichment.py
│   ├── email_enrichment.py
│   ├── personalization.py
│   ├── validation.py
│   ├── outreach.py
│   └── final_dataset.py
│
├── main.py
├── requirements.txt
├── README.md
├── .env
└── .gitignore