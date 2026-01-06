from src.getDataRemote import GetWeatherData
import matplotlib.pyplot as plt

import pandas as pd
from pvlib import pvsystem, modelchain, location, solarposition
import numpy as np

# Define source paths
# Define parameters for calculation
latitude=48.3705
longitude=10.8978

url = 'https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/10_minutes/solar/recent/'
name = '10minutenwerte_SOLAR_00232_akt.zip' 

start_time = '2024-06-21 03:00'
end_time = '2024-06-21 21:00'
tz = 'Etc/GMT'

data = GetWeatherData()

print("Download data")
#data.downloadData(232)
times, gs_values, ds_values = data.loadData(232, start_time=start_time, end_time=end_time)
times_clock = times.dt.strftime("%H:%M")
#print(times_clock.shape)


plt.figure(figsize=(10,5))
plt.plot(times_clock, gs_values, marker="o", linestyle="-")

plt.xlabel("Time")
plt.ylabel("GS_10")
plt.title("GS_10 over Time")
plt.grid(True)
plt.tight_layout()

# --- Save plot ---
plt.savefig("gs10_plot.png", dpi=300)   # You can change filename and format

times = pd.date_range(start_time, end_time, freq='10min',
                      tz=tz)

solar_position = solarposition.get_solarposition(
    times,
    latitude,
    longitude
)

zenith = solar_position['zenith']
zenith[zenith > 85] = 85
# Convert zenith to radians
cos_zenith = np.cos(np.deg2rad(zenith))
cos_zenith.to_csv('zenith_values.txt', sep="\t", index=False)
#print(len(times_clock))
dni_values = ((gs_values*16.6667 - ds_values*16.6667)) / cos_zenith

dni_values[zenith > 85] = 0

df = pd.DataFrame({
    "ghi": (gs_values * 16.6667),
    "dhi": (ds_values * 16.6667),
    "dni": dni_values
}
)

#print(df)

#df['timestamp'] = pd.to_datetime(
#    '2019-01-01 ' + df['timestamp']
#)

# ensure timestamp is datetime
#df['timestamp'] = pd.to_datetime(df['timestamp'])

# set as index
#df = df.set_index('timestamp')

# localize timezone (use the correct tz name if you know it)
#df.index = df.index.tz_localize('Etc/GMT+1')  #df['timestamp'] = df['timestamp'].dt.tz_localize('Europe/Berlin')

# reorder columns
df = df[['ghi', 'dni', 'dhi']]

#print(df)

array_kwargs = dict(
    module_parameters=dict(pdc0=1, gamma_pdc=-0.004),
    temperature_model_parameters=dict(a=-3.56, b=-0.075, deltaT=3)
)

arrays = [
    pvsystem.Array(pvsystem.FixedMount(30, 270), name='West-Facing Array',              
                   **array_kwargs),
    pvsystem.Array(pvsystem.FixedMount(30, 90), name='East-Facing Array',
                   **array_kwargs),
]
#loc = location.Location(40, -80)
loc = location.Location(
    latitude=48,
    longitude=10,
    tz=tz
)

system = pvsystem.PVSystem(arrays=arrays, inverter_parameters=dict(pdc0=3))
mc = modelchain.ModelChain(system, loc, aoi_model='physical',
                           spectral_model='no_loss')

#print(times)
weather = loc.get_clearsky(times)
df.to_csv("output.txt", sep="\t", index=False)

mc.run_model(df)

fig, ax = plt.subplots()
for array, pdc in zip(system.arrays, mc.results.dc):
    pdc.plot(label=f'{array.name}')
#(mc.results.dc[0]).plot(label='Test')
mc.results.ac.plot(label='Inverter')
plt.ylabel('System Output')
plt.legend()
plt.savefig('test.png')

times, gs_values, ds_values = data.loadData(232, start_time=start_time, end_time=end_time, hourly_data=True)
#times_clock = times.dt.strftime("%H:%M")

plt.figure(figsize=(10,5))
plt.plot(np.arange(len(gs_values)), gs_values, marker="o", linestyle="-")

plt.xlabel("Time")
plt.ylabel("GS_10")
plt.title("GS_10 over Time")
plt.grid(True)
plt.tight_layout()
# --- Save plot ---
plt.savefig("gs1h_plot.png", dpi=300)   # You can change filename and format

#print(mc.results.dc[0])



#df["ghi"] = gs_values * 16.6667

#plt.show()