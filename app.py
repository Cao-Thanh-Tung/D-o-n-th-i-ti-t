from flask import Flask, render_template
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import seaborn as sns
from keras import  models,layers,callbacks
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

app = Flask(__name__)

best_model = models.load_model('model_weights.keras')
df = pd.read_csv('final_data.csv')
# df = pd.read_csv('weather_data.csv')

df3 = df.tail(10)
df3['date'] = pd.to_datetime(df3['date'])
df3 = df3[['avg_temp','avg_humidity','avg_dewpoint','avg_windspeed','max_rain_per_minute','day_rainfall','month_rainfall','max_temp','min_temp','max_humidity','min_humidity']]

# Normalize the data
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(df3)

test = np.expand_dims(scaled_data, axis=0)

h = best_model.predict(test)
true_temp = scaler.inverse_transform(h)
true_temp = pd.DataFrame(true_temp)
true_temp.columns = ['avg_temp','avg_humidity','avg_dewpoint','avg_windspeed','max_rain_per_minute','day_rainfall','month_rainfall','max_temp','min_temp','max_humidity','min_humidity']

true_temp = pd.DataFrame(true_temp, columns=['avg_temp','avg_humidity','avg_dewpoint','avg_windspeed','max_rain_per_minute','day_rainfall','month_rainfall','max_temp','min_temp','max_humidity','min_humidity'])

true_temp_dict = true_temp.to_dict(orient='records')
print(true_temp_dict)


def get_wind_direction(degree):
    directions = [
        "Bắc", "Bắc Đông Bắc", "Đông Bắc", "Đông Đông Bắc",
        "Đông", "Đông Đông Nam", "Đông Nam", "Nam Đông Nam",
        "Nam", "Nam Tây Nam", "Tây Nam", "Tây Tây Nam",
        "Tây", "Tây Tây Bắc", "Tây Bắc", "Bắc Tây Bắc"
    ]
    index = round(degree / 22.5) % 16
    return directions[index]

@app.route('/')
def hello_world():
    last_row = df.tail(1)

    if 'avg_direction' in last_row:
        today = last_row.to_dict(orient='records')[0]
        wind_direction = get_wind_direction(today['avg_direction'])
    else:
        today = {}
        wind_direction = None

    return render_template('index.html', today=today, direction=wind_direction, tomorrow=true_temp_dict[0])

if __name__ == '__main__':
    app.run(debug=True)
