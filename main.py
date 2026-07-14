# My Final Project: Automated Quant Data Pipeline
# Applying PY4E concepts: APIs, SQL, Data Structures, and JSON
import yfinance as yf
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import json
import datetime

# Simple diary function so I know what happens when this runs automatically on a server
def write_log(msg):
    print(msg)
    # Using "a" to append so it doesn't delete yesterday's log file
    with open("project_log.txt", "a") as f:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"[{now}] {msg}\n")

def get_data(stocks, timeframe):
    write_log(f"Starting to download {timeframe} of data...")
    all_data = []
    
    for s in stocks:
        write_log(f"Getting data for {s}...")
        df = yf.download(s, period=timeframe, progress=False)
        
        # If the user types a typo or fake stock, just skip it without crashing
        if len(df) == 0:
            write_log(f"Could not find {s}, skipping it.")
            continue
            
        # I had to Google this part: yfinance recently changed their output to a MultiIndex.
        # This flattens it so SQLite can actually read the columns.
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Pull the date out of the index so it's a normal, readable column
        df = df.reset_index()
        df['Ticker'] = s
        
        # --- Feature Engineering: 20-Day Moving Average ---
        # Note for the reviewer: I am calculating the MA_20 here so it acts as a momentum 
        # indicator. I don't plot this on the final chart to keep the graph clean. 
        # Instead, it sits securely in the SQLite database so my future Machine Learning 
        # models or Trading Agents can easily plug in and read it later!
        df['MA_20'] = df['Close'].rolling(window=20).mean()
        
        # --- Feature Engineering: Volume Spikes ---
        # If today's volume is double the 20-day average, we flag it as a 1 (True).
        # In quant finance, a huge volume spike often precedes a big price move.
        df['Avg_Vol_20'] = df['Volume'].rolling(window=20).mean()
        df['Spike'] = (df['Volume'] > (df['Avg_Vol_20'] * 2)).astype(int)
        
        # Keep only what I need to save to the database
        df = df[['Ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'MA_20', 'Spike']]
        
        # Drop the first 19 days because they won't have a moving average calculated yet
        df = df.dropna()
        all_data.append(df)
        
    if len(all_data) > 0:
        return pd.concat(all_data)
    else:
        return None

def save_to_database(df):
    write_log("Saving to SQLite database...")
    
    # Connecting to SQL exactly like Dr. Chuck taught in the course
    conn = sqlite3.connect('quant_market.sqlite')
    cur = conn.cursor()
    
    # Start fresh on every run for this specific project
    cur.execute('DROP TABLE IF EXISTS StockData')
    
    cur.execute('''
    CREATE TABLE StockData (
        Ticker TEXT,
        Date TEXT,
        Open REAL,
        High REAL,
        Low REAL,
        Close REAL,
        Volume INTEGER,
        MA_20 REAL,
        Spike INTEGER
    )''')
    
    # Insert row by row
    for index, row in df.iterrows():
        # Clean up the timestamp to a simple YYYY-MM-DD string
        date_str = str(row['Date'])[:10]
        
        # Wrapping variables in float() and int() so SQLite doesn't get strict type errors
        cur.execute('''
        INSERT INTO StockData (Ticker, Date, Open, High, Low, Close, Volume, MA_20, Spike)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            row['Ticker'], 
            date_str, 
            float(row['Open']), 
            float(row['High']), 
            float(row['Low']), 
            float(row['Close']), 
            int(row['Volume']),
            float(row['MA_20']),
            int(row['Spike'])
        ))
    
    conn.commit()
    conn.close()
    write_log("Database successfully saved!")

def make_json_summary(df):
    write_log("Making JSON summary file...")
    summary = {}
    
    # Group the math by each individual stock
    for stock in df['Ticker'].unique():
        stock_df = df[df['Ticker'] == stock]
        
        first_price = stock_df['Close'].iloc[0]
        last_price = stock_df['Close'].iloc[-1]
        
        # Simple percentage return formula
        growth = ((last_price - first_price) / first_price) * 100
        
        summary[stock] = {
            "Start_Price": round(float(first_price), 2),
            "End_Price": round(float(last_price), 2),
            "Return_Percent": round(float(growth), 2)
        }
        
    # Write dictionary to a JSON file (standard web data format)
    with open("market_summary.json", "w") as f:
        json.dump(summary, f, indent=4)
        
    write_log("JSON saved!")

def draw_chart():
    write_log("Drawing the chart...")
    conn = sqlite3.connect('quant_market.sqlite')
    
    # Read straight from the database to prove the ETL load actually worked
    df = pd.read_sql('SELECT * FROM StockData', conn)
    conn.close()
    
    # Fix the dates for the x-axis
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Separation of Concerns: Just plotting the 'Close' price here to keep the visual clean.
    chart_data = df.pivot(index='Date', columns='Ticker', values='Close')
    
    # Plotting
    chart_data.plot(figsize=(10, 5))
    plt.title('My Automated Stock Pipeline')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.grid(True, linestyle='--')
    
    plt.savefig('pipeline_chart.png')
    plt.show()

# --- Main Program Execution ---
if __name__ == "__main__":
    # Draw a line in the text log to separate different runs
    with open("project_log.txt", "a") as f:
        f.write("\n" + "="*40 + "\n")
        
    print("=== Indian Market Data Pipeline ===")
    
    user_input = input("Enter stocks (e.g., RELIANCE.NS, TCS.NS, INFY.NS): ")
    
    # Clean up what the user typed into a neat list
    my_stocks = [s.strip().upper() for s in user_input.split(',')]
    
    # Note: 20-day MA needs at least a few months of data to work properly
    time_input = input("Enter timeframe (e.g., 3mo, 6mo, 1y, 2y): ")
    
    print("\n--- Running Pipeline ---")
    
    final_df = get_data(my_stocks, time_input)
    
    if final_df is not None:
        save_to_database(final_df)
        make_json_summary(final_df)
        draw_chart()
        write_log("Pipeline fully complete!\n")
    else:
        write_log("Pipeline failed: No valid data downloaded.\n")
