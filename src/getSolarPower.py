import numpy as np
import pvlib
import pandas as pd

from pvlib import pvsystem, modelchain, location, solarposition

class GetSolarPower:
    def __init__(self, latitude=48, longitude=10, tz='Etc/GMT'):
        self.latitude = latitude
        self.longitude = longitude
        self.tz = tz
        # Array needs to be initialized before usage 
        self.solar_array = []

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

    def setSolarArraySystem(self, panel_orientation=None, names=None, 
                            modules_per_string=None, strings=None):
        """
        Configure the solar array system definition.

        Args:
            panel_orientation (list[list[float]], optional):
                Each element must be [tilt, azimuth].
                Example: [[30, 270], [30, 90]]
            names (list[str], optional):
                Human readable array names.
            modules_per_string (list[int], optional):
                Number of modules per string for each array.
            strings (list[int], optional):
                Number of strings for each array.

        Raises:
            TypeError: If input types are incorrect.
            ValueError: If lists are not equal length or values invalid.

        Returns:
            None
        """

        # set default values if required 
        if panel_orientation is None:
            panel_orientation = [[30, 270],[30, 90]]
        if names is None:
            names = ['West-Facing Array', 'East-Facing Array']
        if modules_per_string is None:
            modules_per_string = [1, 1]
        if strings is None:
            strings = [1, 1]

        # ----- basic type checks -----
        if not isinstance(panel_orientation, list):
            raise TypeError("panel_orientation must be a list")

        if not isinstance(names, list):
            raise TypeError("names must be a list")

        if not isinstance(modules_per_string, list):
            raise TypeError("modules_per_string must be a list")

        if not isinstance(strings, list):
            raise TypeError("strings must be a list")

        # ----- same length check -----
        lists = [panel_orientation, names, modules_per_string, strings]
        if len({len(lst) for lst in lists}) != 1:
            raise ValueError(
                "panel_orientation, names, modules_per_string, and strings must all have the same length"
            )

        n = len(panel_orientation)

        # ----- structure + content checks -----

        # panel_orientation: list of [tilt, azimuth]
        for i, item in enumerate(panel_orientation):
            if not isinstance(item, list):
                raise TypeError(f"panel_orientation[{i}] must be a list like [tilt, azimuth]")
            if len(item) != 2:
                raise ValueError(f"panel_orientation[{i}] must contain exactly 2 values")
            tilt, azimuth = item
            if not (isinstance(tilt, (int, float)) and isinstance(azimuth, (int, float))):
                raise TypeError(f"panel_orientation[{i}] values must be numeric")

        # names: list of strings
        for i, name in enumerate(names):
            if not isinstance(name, str):
                raise TypeError(f"names[{i}] must be a string")

        # modules_per_string: list of positive ints
        for i, m in enumerate(modules_per_string):
            if not isinstance(m, int) or m <= 0:
                raise ValueError(f"modules_per_string[{i}] must be a positive integer")

        # strings: list of positive ints
        for i, s in enumerate(strings):
            if not isinstance(s, int) or s <= 0:
                raise ValueError(f"strings[{i}] must be a positive integer")


        # Create solor array definition based on the inputs 
        for count, panel_dir in enumerate(panel_orientation):

            array_kwargs = dict(
                module_parameters=dict(pdc0=1, gamma_pdc=-0.004),
                temperature_model_parameters=dict(a=-3.56, b=-0.075, deltaT=3), 
                modules_per_string=modules_per_string[count], 
                strings=strings[count]
            )

            self.solar_array.append(pvsystem.Array(pvsystem.FixedMount(panel_dir[0], panel_dir[1]), name=names[count], **array_kwargs))


    def runSolarSystem(self):
        # Check if solor array was already configured
        if not self.solar_array:
            raise ValueError("Solar array system is not correctly configured")
        
        system = pvsystem.PVSystem(arrays=self.solar_array, inverter_parameters=dict(pdc0=3))
        mc = modelchain.ModelChain(system, self.loc, aoi_model='physical',
                                spectral_model='no_loss')
        return mc