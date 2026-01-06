# Example: Python (requires pvlib, pandas, numpy)
import pvlib
import pandas as pd
import numpy as np

# --- 1) Inputs (example)
lat, lon, tz = 50.0, 8.5, 'Europe/Berlin'   # change to site coords
surface_tilt = 30.0     # deg
surface_azimuth = 180.0 # 180 = south
system_capacity_kw = 10.0  # nameplate DC kW

# df: pandas DataFrame with index tz-aware and columns: 'ghi', 'temp_air', 'wind_speed'
# Example: df = pd.read_csv('dwd_station_hourly.csv', parse_dates=['time'], index_col='time').tz_localize('Europe/Berlin')

# --- 2) solar position
solpos = pvlib.solarposition.get_solarposition(df.index, lat, lon)
df['solar_zenith'] = solpos['zenith']
df['solar_azimuth'] = solpos['azimuth']

# --- 3) Decompose GHI -> DNI, DHI (Erbs)
dni_dhi = pvlib.irradiance.erbs(df['ghi'], df['solar_zenith'], df.index.hour)
df['dni'] = dni_dhi['dni']
df['dhi'] = dni_dhi['dhi']

# --- 4) POA: beam/diffuse/ground + AOI, using Perez transposition
aoi = pvlib.irradiance.aoi(surface_tilt, surface_azimuth,
                           df['solar_zenith'], df['solar_azimuth'])
poa = pvlib.irradiance.get_total_irradiance(surface_tilt,
                                            surface_azimuth,
                                            df['solar_zenith'],
                                            df['solar_azimuth'],
                                            df['dni'],
                                            df['ghi'],
                                            df['dhi'],
                                            model='perez')
df['poa_global'] = poa['poa_global']
df['poa_direct'] = poa['poa_beam']
df['poa_diffuse'] = poa['poa_sky_diffuse'] + poa['poa_ground_diffuse']

# --- 5) Module temperature (pvsyst model)
df['temp_module'] = pvlib.temperature.pvsyst_cell(poa_global=df['poa_global'],
                                                  temp_air=df['temp_air'],
                                                  wind_speed=df['wind_speed'])

# --- 6) DC power (pvwatts) and AC (pvwatts inverter)
# pvwatts expects irradiance in W/m2 and temp cell in C
dc = pvlib.pvsystem.pvwatts_dc(df['poa_global'], df['temp_module'],
                               system_capacity_kw * 1000,
                               pdc0=system_capacity_kw * 1000)
# pvwatts_dc returns per-array DC; convert to kW and then AC
df['dc_power_kw'] = dc / 1000.0
df['ac_power_kw'] = pvlib.inverter.pvwatts(df['dc_power_kw'] * 1000) / 1000.0  # if using pvlib inverter pvwatts helper

# --- 7) Energy
df['energy_kwh'] = df['ac_power_kw'] * (1.0)  # hourly data -> kW * 1 h = kWh
annual_yield_kwh = df['energy_kwh'].sum()
print(f"Annual energy (kWh): {annual_yield_kwh:.0f}")
