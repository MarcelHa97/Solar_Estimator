import numpy as np
import pvlib
import pandas as pd

from pvlib import pvsystem, modelchain, location, solarposition

class GetSolarPower:
    def __init__(self, latitude=48, longitude=10, tz='Etc/GMT'):
        self.latitude = latitude
        self.longitude = longitude
        self.tz = tz

        # set location of the solar arry
        self.loc = location.Location(
            latitude=latitude,
            longitude=longitude,
            tz=tz
        )

    def setLocation(self, latitude, longitude, time_zone):
        # Set time zone and location parameters
        self.latitude = latitude
        self.longitude = longitude
        self.tz = time_zone
        
        # set location of the solar array
        self.loc = location.Location(
            latitude=latitude,
            longitude=longitude,
            tz=time_zone
        )

    def setSolarSystem(self, num_arrays):
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
     
        system = pvsystem.PVSystem(arrays=arrays, inverter_parameters=dict(pdc0=3))
        mc = modelchain.ModelChain(system, self.loc, aoi_model='physical',
                                spectral_model='no_loss')
        
        return mc