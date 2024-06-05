import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import seaborn as sns
# from keras import  models,layers,callbacks
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

from tensorflow.keras import models, layers, callbacks
from tensorflow.keras.initializers import Orthogonal
from tensorflow.keras.models import load_model

custom_objects = {'Orthogonal': Orthogonal}
best_model = load_model('model_weights.keras', custom_objects=custom_objects)
# best_model = models.load_model('model_weights.keras')
print("hello")
df = pd.read_csv('final_data.csv')

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
print(true_temp)
