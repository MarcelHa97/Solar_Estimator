import numpy as np
import pvlib
import pandas as pd
import os
import shutil

import urllib.request
import zipfile

class GetWeatherData:
    def __init__(self, data_path='./data/weather_data/', 
                 url='https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/10_minutes/solar/recent/', 
                 station_ids=[232, 691, 2522, 1262]):
        self.data_path = data_path
        self.url = url
        self.station_ids = station_ids
        
        
    def downloadData(self, station_id):
        if station_id in self.station_ids:
            print("Station ID is correct!")
        else:
            print("Station ID is incorrect!")
            return 0
        
        file_name = '10minutenwerte_SOLAR_' + str(station_id).zfill(5) + '_akt.zip'
        dir_path = self.data_path + file_name
        url_file = self.url + file_name

        # Remove old directory
        shutil.rmtree((self.data_path + '10minutenwerte_SOLAR_' + str(station_id).zfill(5)))

        # Download file from remote server
        urllib.request.urlretrieve(url_file, dir_path)

        # Unzip file 
        zip_path = self.data_path + file_name     # path to your .zip file
        extract_to = self.data_path + '10minutenwerte_SOLAR_' + str(station_id).zfill(5)   # folder where files will be extracted

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)


    def loadData(self, station_id, start_time = "2025-11-22 06:00", end_time = "2025-11-22 17:00", hourly_data = False, data_type = "GS_10"):
        dir_name = '10minutenwerte_SOLAR_' + str(station_id).zfill(5)
        dir_path = self.data_path + dir_name + '/' + os.listdir((self.data_path + dir_name))[0]
        #df = pd.read_csv('dwd_station_hourly.csv', parse_dates=['time'], index_col='time').tz_localize('Europe/Berlin')
        data = pd.read_csv(dir_path, sep=";", skipinitialspace=True)
        data = data.drop(columns=["eor"])
        data["MESS_DATUM"] = pd.to_datetime(data["MESS_DATUM"], format="%Y%m%d%H%M")

        # Read data from file
        start_t = pd.to_datetime(start_time)
        end_t   = pd.to_datetime(end_time)

        mask = (data["MESS_DATUM"] >= start_t) & (data["MESS_DATUM"] <= end_t)
        subset = data.loc[mask]

        if hourly_data:
            gs_values = subset["GS_10"].to_numpy()
            # Ensure length is a multiple of 6
            n_hours = len(gs_values) // 6
            gs_trimmed = gs_values[:n_hours * 6]
            # Reshape and sum
            gs_values = gs_trimmed.reshape(-1, 6).sum(axis=1)

            ds_values = subset["DS_10"].to_numpy()
            # Ensure length is a multiple of 6
            n_hours = len(ds_values) // 6
            ds_trimmed = ds_values[:n_hours * 6]
            # Reshape and sum
            ds_values = ds_trimmed.reshape(-1, 6).sum(axis=1)

            hourly = (
                subset
                .set_index("MESS_DATUM")
                .resample("h")
                .sum()
            )

            times = hourly.index
            times = times[1:-1]
        else:
            gs_values = subset["GS_10"].to_numpy()
            ds_values = subset["DS_10"].to_numpy()
            times = subset["MESS_DATUM"]

        return times, gs_values, ds_values

        