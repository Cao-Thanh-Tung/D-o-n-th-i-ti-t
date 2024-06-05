from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from datetime import datetime
import os

mapping_array = ["avg_temp", "avg_humidity", "avg_dewpoint", "avg_barometer", "avg_windspeed", "avg_gustspeed", "avg_direction", "month_rainfall", "year_rainfall", "max_rain_per_minute", "max_temp", "min_temp", "max_humidity", "min_humidity", "max_pressure", "min_pressure", "max_windspeed", "max_gustspeed", "max_heat_index"]
Dates_r = pd.date_range(start='01/01/2010', end='05/31/2024', freq='M')
dates = [str(i)[:4] + str(i)[5:7] for i in Dates_r]
all_data = []
all_indices = []

for k in range(len(dates)):
    url = 'https://www.estesparkweather.net/archive_reports.php?date=' + dates[k]
    print("Start crawl link: " + url)
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

        df_list.append(c)
        if len(c) > 0:
            all_indices.append(dates[k] + c[0])

    # Filter and process indices
    f_index = [index for index in all_indices if len(index) > 6]
    final_index = [datetime.strptime(str(f_index[i]), '%Y%m%d').strftime('%Y-%m-%d') for i in range(len(f_index))]
    # Filter and process data
    data = [df_list[i][1:] for i in range(len(df_list)) if len(df_list[i][1:]) == 19]
    all_data.extend(data)

# Make sure data and indices lengths match
if len(all_data) == len(final_index):
    df = pd.DataFrame(all_data, index=final_index, columns=mapping_array)
    file_path = 'weather_data.csv'

    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        existing_df = pd.read_csv(file_path, index_col=0)
        combined_df = pd.concat([existing_df, df])
        combined_df.to_csv(file_path, index=True)
    else:
        df.to_csv(file_path, index=True)

    print("Data has been saved to weather_data.csv")
else:
    print(f"Data length: {len(all_data)}, Index length: {len(final_index)}")
    print("Data and indices length mismatch, please check the data source or processing logic.")
