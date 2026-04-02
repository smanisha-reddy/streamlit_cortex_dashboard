<<<<<<< HEAD
# Streamlit Cortex Dashboard

A Streamlit-based sales analytics dashboard integrated with Snowflake for data retrieval and Snowflake Cortex for AI-generated business summaries.

## Overview

This project demonstrates how to build an interactive sales analytics dashboard using Streamlit and Snowflake. It supports secure MFA-based authentication, interactive business filtering, KPI tracking, chart-based trend analysis, and AI-generated sales summaries using Snowflake Cortex.

The dashboard is designed for local development and testing, with configuration managed through local TOML files for both Streamlit and Snowflake CLI/Cortex CLI usage.

---

## Features

### Dashboard and Analytics
- KPI cards for:
  - Total Sales
  - Total Orders
  - Total Quantity
  - Average Order Value
- Interactive filtering by:
  - Region
  - Category
  - Customer Type
  - Sales Channel
  - Order Date Range
- Visual analysis for:
  - Sales by Region
  - Sales by Category
  - Sales Trend by Date
  - Top Products
  - Sales by Channel
- Filtered sales data table for detailed review

### AI Summary
- Generates an AI-based sales summary using Snowflake Cortex
- Uses `SNOWFLAKE.CORTEX.COMPLETE(...)` from within Snowflake SQL
- Summarizes filtered results into business-friendly insights and recommendations

### Security and Authentication
- Uses Snowflake username/password authentication with MFA passcode
- Keeps credentials outside application code using local secrets files
- Supports separate connection settings for:
  - Streamlit application execution
  - Snowflake CLI / Cortex Code CLI usage

---

## Tech Stack

- Python
- Streamlit
- Pandas
- Snowflake Python Connector
- Snowflake Cortex
- Snowflake CLI / Cortex Code CLI

---

## Project Structure

```text
streamlit_cortex_dashboard/
├── .streamlit/
│   ├── secrets.toml
│   └── secrets.example.toml
├── .snowflake/
│   ├── connections.toml
│   └── connections.example.toml
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Quick Start

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```
=======
# streamlit_cortex_dashboard
Interactive Streamlit sales analytics dashboard built with Python and Snowflake, and enhanced using Cortex Code CLI for prompt-driven code updates, UI improvements, and development acceleration.
>>>>>>> 6d1a9808478eebc0f07a8453c5ea12ae30cb0b62
