# 📈 Automated Quant Data Pipeline

An end-to-end ETL (Extract, Transform, Load) pipeline designed to extract market data, engineer quantitative features, and securely store structured data for algorithmic trading agents. 

This project was built to bridge the gap between foundational programming concepts and real-world quantitative finance infrastructure.

## 🚀 Core Architecture & Engineering Principles

### 1. Feature Engineering (Momentum & Volume)
Raw market prices are insufficient for predictive modeling or algorithmic trading. This pipeline automatically transforms incoming data by calculating:
* **20-Day Moving Average (MA_20):** Captures short-term monthly momentum to smooth out daily market noise.
* **Volume Spikes:** A binary flag (1 or 0) for trading days where volume exceeds double the 20-day historical average, often indicating significant institutional market moves.

### 2. Separation of Concerns
To maintain system integrity, visualization and data storage are strictly isolated:
* **Visualization:** Generates a clean, readable line chart showing only the closing prices.
* **Database (SQLite):** Securely stores all raw prices *and* the newly engineered features. This acts as a centralized, machine-readable "source of truth" allowing future trading algorithms and machine learning models to query the data instantly.

### 3. Autonomous System Logging
Designed for automated server execution (e.g., via Cron jobs), the pipeline features a built-in `project_log.txt` generator. It timestamps API requests, tracks skipped/missing data, and monitors system health for easy background debugging without human oversight.

### 4. JSON Serialization
Automatically calculates the total percentage return for all queried assets and exports a serialized `market_summary.json` file for lightweight web, API, or dashboard integration.

## 🛠️ Tech Stack
* **Python 3** (Core Pipeline Logic)
* **Pandas** (Data Transformation & Rolling Calculations)
* **SQLite3** (Relational Database Management)
* **yfinance API** (Data Extraction)
* **Matplotlib** (Data Visualization)

---

## 📖 Quick-Start User Manual

This tool is designed to instantly pull, engineer, and store high-quality financial data on your local machine. Follow these 5 simple steps to run the pipeline yourself.

### Step 1: Prerequisites
Ensure you have Python installed on your computer along with the necessary data engineering libraries. Open your terminal and run:
`pip install -r requirements.txt`
*(Alternatively, install manually: `pip install pandas yfinance matplotlib`)*

### Step 2: Launch the Program
Run the main Python script in your terminal or IDE:
`python main.py`

### Step 3: Provide Your Inputs
The terminal will ask for two specific inputs:
* **The Tickers:** Type the stock symbols you want to analyze, separated by commas. 
  * *Example:* `RELIANCE.NS, TCS.NS, INFY.NS` (Use the `.NS` suffix for Indian stocks on Yahoo Finance).
* **The Timeframe:** Type how far back you want the data to go. 
  * *Example:* `3mo`, `6mo`, `1y`, `2y`. *(Note: Because the program calculates a 20-Day Moving Average, please choose a timeframe of at least 3 months).*

### Step 4: Monitor the Execution
The pipeline will run autonomously. You will see real-time updates in your terminal as it fetches the data, calculates the momentum indicators, and saves the database. 

### Step 5: Review Your Outputs
When the pipeline finishes, look inside your project folder to find your four generated outputs:
1. `quant_market.sqlite`: The master database containing all raw prices and engineered features.
2. `market_summary.json`: A web-ready summary detailing the starting price, ending price, and total percentage return.
3. `pipeline_chart.png`: A saved image of the visual data graph.
4. `project_log.txt`: The timestamped system execution log.
