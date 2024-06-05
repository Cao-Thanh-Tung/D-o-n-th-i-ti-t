from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from datetime import datetime, timedelta
import os

from Clean_process_data import clean_data


def crawl(start_date, end_date):
    mapping_array = ["avg_temp", "avg_humidity", "avg_dewpoint", "avg_barometer", "avg_windspeed", "avg_gustspeed",
                     "avg_direction", "month_rainfall", "year_rainfall", "max_rain_per_minute", "max_temp", "min_temp",
                     "max_humidity", "min_humidity", "max_pressure", "min_pressure", "max_windspeed", "max_gustspeed",
                     "max_heat_index"]
    Dates_r = pd.date_range(start=start_date, end=end_date, freq='D')
    dates = [date.strftime('%Y%m%d') for date in Dates_r]
    all_data = []
    all_indices = []

    for date in dates:
        url = 'https://www.estesparkweather.net/archive_reports.php?date=' + date[:6]
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        table = soup.find_all('table')
        raw_data = [row.text.splitlines() for row in table]
        raw_data = raw_data[:-9]

        for i in range(len(raw_data)):
            raw_data[i] = raw_data[i][2:len(raw_data[i]):3]

        df_list = []
        for i in range(len(raw_data)):
            c = ['.'.join(re.findall(r"\d+", str(raw_data[i][j].split()[:5]))) for j in range(len(raw_data[i]))]
            if len(c) > 0 and c[0] == date[6:]:
                df_list.append(c)
                all_indices.append(datetime.strptime(date, '%Y%m%d').strftime('%Y-%m-%d'))

        # Filter and process data
        data = [df_list[i][1:] for i in range(len(df_list)) if len(df_list[i][1:]) == 19]
        all_data.extend(data)

    # Check if there is any new data
    if not all_data:
        print("No new data available to crawl.")
        return

    # Make sure data and indices lengths match
    if len(all_data) == len(all_indices):
        df = pd.DataFrame(all_data, index=all_indices, columns=mapping_array)
        file_path = 'weather_data.csv'

        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            existing_df = pd.read_csv(file_path, index_col=0, parse_dates=True)
            last_date_in_csv = existing_df.index[-1].strftime('%Y-%m-%d')
            if all_indices and all_indices[-1] <= last_date_in_csv:
                print("No new data available to add.")
                return
            combined_df = pd.concat([existing_df, df]).drop_duplicates()
            combined_df.index = pd.to_datetime(combined_df.index).strftime('%Y-%m-%d')
            combined_df.to_csv(file_path, index=True)
        else:
            df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d')
            df.to_csv(file_path, index=True)

        print("Data has been saved to weather_data.csv")
        clean_data('weather_data.csv', 'final_data.csv')
    else:
        print(f"Data length: {len(all_data)}, Index length: {len(all_indices)}")
        print("Data and indices length mismatch, please check the data source or processing logic.")


def auto_crawl():
    # Step 1: Get today's date
    today = datetime.today().strftime('%Y-%m-%d')
    yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

    # Step 2: Read the last line from the csv file to get the most recent date
    file_path = 'weather_data.csv'
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        df = pd.read_csv(file_path, index_col=0, parse_dates=True)
        last_date = df.index[-1].strftime('%Y-%m-%d')
    else:
        last_date = '2010-01-01'  # Default start date if file does not exist

    # Step 3: Check if today's date or yesterday's date is different from the last date in the file
    last_date_dt = datetime.strptime(last_date, '%Y-%m-%d')
    today_dt = datetime.strptime(today, '%Y-%m-%d')
    yesterday_dt = datetime.strptime(yesterday, '%Y-%m-%d')

    if today_dt > last_date_dt or yesterday_dt > last_date_dt:
        # Ensure the start date for crawling is the beginning of the next day after the last date
        start_date = (last_date_dt + timedelta(days=1)).strftime('%Y-%m-%d')
        print(f"Crawling data from {start_date} to {today}")
        crawl(start_date, today)
    else:
        print("Data is already up-to-date")



auto_crawl()
