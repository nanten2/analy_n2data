#!/usr/bin/env python
import astropy.units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_body, FK5
from astropy.time import Time
from datetime import datetime
import kisa_rev
import numpy

#Parameter
latitude = -22.96995611
longitude = -67.70308139
height = 4863.85
nanten2 = EarthLocation(lat = latitude*u.deg, lon = longitude*u.deg, height = height*u.m)

#path
hosei = "/home/amigos/ros/src/necst/lib/hosei_230.txt"
#hosei = "./hosei_copy.txt"

def __e(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")

def fk5_from_altaz(az, el, obstime):
    #type check
    #obstime unix time    
    #note
    #pressure needs
    #kisa calc
    delta = []
    for i in range(len(az)):
        delta.append(kisa_rev.apply_kisa_test(az[i]/3600., el[i]/3600., hosei))
    #for broadcasting
    delta = numpy.array(delta)
    delta = delta.transpose((1,0))
    az = numpy.array(az) 
    el = numpy.array(el)
    tmp_pressure = 0*u.Pa
    dt = [datetime.utcfromtimestamp(i) for i in obstime]
    dd = list(map(__e, dt))
    _time = Time(dd, scale = "utc")
    print("Az", az)#Az
    print("El", el)#El
    print(delta)
    az = az + delta[0]/3600
    el = el + delta[1]/3600
    on_skycoord = SkyCoord(az, el, frame = "altaz", unit = "deg", location = nanten2, obstime = _time, pressure = tmp_pressure)
    t = on_skycoord.transform_to(FK5)
    return t.ra, t.dec
