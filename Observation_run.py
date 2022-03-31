# File to produce an output Excel sheet with Observation information of the given targets.

# The way this is going to work is that the user that wants to conduct observations, needs
# to write all the pre requisite information like the observatory location, targets, constraints etc in
# the inputs files given in the ./inputs folder json files. The parse_input files then parses it.
# this file will take functions from parse_input and use its outputs here.

# Important Libraries.

import numpy as np
import pytz
import matplotlib.pyplot as plt
import astropy.units as u
import numpy as np
import pandas as pd
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
from astroplan import Observer, FixedTarget
from astropy.utils.iers import conf
from astroplan import download_IERS_A
from astropy.coordinates import get_sun, get_moon, get_body
from astroplan import moon_illumination  # made 0 duo to an error
import parse_input as pi
import os
from astroplan import (
    AltitudeConstraint,
    AirmassConstraint,
    AtNightConstraint,
    MoonSeparationConstraint,
)
from astroplan import is_observable, is_always_observable, months_observable

conf.auto_max_age = None

input_file_path = "./inputs/input.json"

# using UTI1
download_IERS_A()


def time_in_india():
    """
    Arguements: None
    Returns: The time in India Now
    """
    date = now + 5 * u.h + 30 * u.min
    return date


def target_is_up(observer, target, time_of_observation):
    is_up = observer.target_is_up(time_of_observation, target)
    return is_up


def target_fix_icrs(longitude, latitude):  # International Celestial Reference System
    coords = SkyCoord(longitude, latitude, frame="icrs")
    return coords


def altitude(observer, time_of_observation, target):
    alt = observer.altaz(time_of_observation, target)
    return alt.alt.degree


def azimuth(observer, time_of_observation, target):
    az = observer.altaz(time_of_observation, target)
    return az.az.degree


def moon():
    return get_moon(now)


def moon_illumination_today():
    return moon_illumination(now)


def airmass(observer, time_of_observation, target):
    target_altaz = observer.altaz(time_of_observation, target)
    return target_altaz.secz


def observation_time_set(start, end, observer):
    observation_time = start + (end - start) * np.linspace(0.0, 1.0, 20)
    return observation_time


def x_degree_horizon(observer, target, degree):
    time = observer.target_rise_time(
        now, target, which="next", horizon=degree * u.deg
    ).iso
    return time


def rise_time(observer, target):
    time = observer.target_rise_time(now, target).iso
    return time


def set_time(observer, target):
    time = observer.target_set_time(now, target).iso
    return time


def observer_info(observer, obs_time):
    observer_info = pd.DataFrame(columns=["Name", "Date and Time"])

    sunset_ioMIT = observer.sun_set_time(obs_time, which="nearest")
    eve_twil_ioMIT = observer.twilight_evening_astronomical(obs_time, which="nearest")
    midnight_ioMIT = observer.midnight(obs_time, which="nearest")
    morn_twil_ioMIT = observer.twilight_morning_astronomical(obs_time, which="nearest")
    sunrise_ioMIT = observer.sun_rise_time(obs_time, which="next")

    # Adding rows to the Output info file database
    observer_info.loc[0] = ["Nearest Sunset Time", sunset_ioMIT.iso]
    observer_info.loc[1] = ["Nearest Evening Twilight Time", eve_twil_ioMIT.iso]
    observer_info.loc[2] = ["Nearest Midnight Time", midnight_ioMIT.iso]
    observer_info.loc[3] = ["Nearest Morning Twilight Time", morn_twil_ioMIT.iso]
    observer_info.loc[4] = ["Next Sunrise Time", sunrise_ioMIT.iso]

    return observer_info


def main():
    """
    what does the main function do
    """
    # defining the observation time by using the functions from parse_input.py
    # this defines the date and time of the observation, and is an Astropy Time object.
    obs_time = pi.date_and_time_setup(input_file_path)

    # Defining our observer using the function from parse_input file
    # other inputs also to be done like this, and therefore shift some above defined functions to
    # the parse_input file. Thereby eliminating all required TUI from the user side.
    observer = pi.observatory_setup(input_file_path)

    # Getting Key Times, and saving them to an observer info file.
    observer_info_db = observer_info(observer, obs_time)
    observer_info_db.to_csv(os.path.join(os.getcwd(), "outputs/Observer_info.csv"))
    print("Observer Info File Saved!")

    # Constraints is a dictionary containing all the constraints defind in constraints.json
    constraints = pi.constraints_setup(input_file_path)

    # Create a dataframe that has information about the targets using input files.
    target_info_df = pi.targets_setup(input_file_path, observer, constraints, obs_time)

    # os.path is being used so as to maintain consistancy between OSX and Windows devices.
    target_info_df.to_csv(os.path.join(os.getcwd(), "outputs/targets_info.csv"))
    print("Targets Info File Saved!")


main()
