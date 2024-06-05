import pandas as pd


def clean_data(file_path, output_path):
    # Đọc dữ liệu từ file CSV
    data = pd.read_csv(file_path)

    # Đổi tên cột 'Unnamed: 0' thành 'date'
    data.rename(columns={'Unnamed: 0': 'date'}, inplace=True)
    data['date'] = pd.to_datetime(data['date'])

    # Tính toán lượng mưa hàng ngày
    day_rain = []
    day_rain.append(0.0)
    year = data['date'][0].year
    for i in range(len(data) - 1):
        if data['date'][i].year != year:
            year = data['date'][i].year
            day_rain.append(0.0)
        else:
            mm = data['year_rainfall'][i + 1] - data['year_rainfall'][i]
            day_rain.append(round(mm, 2))

    # Đảm bảo không có giá trị âm cho lượng mưa hàng ngày
    day_rain = [0.0 if rain < 0 else rain for rain in day_rain]
    data.insert(8, "day_rainfall", day_rain, True)

    # Gán nhãn 'Rain' hoặc 'No Rain' dựa trên lượng mưa hàng ngày
    labels = ["Rain" if rain > 0.0 else "No Rain" for rain in day_rain]
    data.insert(21, "weather_code", labels, True)

    # Hàm chuyển đổi từ Fahrenheit sang Celsius
    def fahrenheit_to_celsius(f):
        return (float(f) - 32.0) / 1.8

    # Chuyển đổi nhiệt độ từ Fahrenheit sang Celsius
    for i in range(len(data['avg_temp'])):
        avg_temp = round(fahrenheit_to_celsius(data['avg_temp'][i]), 2)
        max_temp = round(fahrenheit_to_celsius(data['max_temp'][i]), 2)
        min_temp = round(fahrenheit_to_celsius(data['min_temp'][i]), 2)
        avg_dewpoint = round(fahrenheit_to_celsius(data['avg_dewpoint'][i]), 2)
        data.at[i, 'avg_temp'] = avg_temp
        data.at[i, 'max_temp'] = max_temp
        data.at[i, 'min_temp'] = min_temp
        data.at[i, 'avg_dewpoint'] = avg_dewpoint

    # Chuyển đổi lượng mưa từ inch sang mm
    data['max_rain_per_minute'] = data['max_rain_per_minute'].apply(lambda x: round(float(x) * 25.4, 2))
    data['month_rainfall'] = data['month_rainfall'].apply(lambda x: round(float(x) * 25.4, 2))
    data['day_rainfall'] = data['day_rainfall'].apply(lambda x: round(float(x) * 25.4, 2))
    data['year_rainfall'] = data['year_rainfall'].apply(lambda x: round(float(x) * 25.4, 2))

    # Lưu dữ liệu đã được làm sạch vào file CSV mới, giữ lại cột chỉ số
    data.to_csv(output_path, index=True)
    print(f"Data has been cleaned and saved to {output_path}")



