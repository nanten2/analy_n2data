#! /usr/bin/env python3
#-*- coding: utf-8 -*-

#import csv
#from pyslalib import slalib
from datetime import datetime as dt
from astropy.coordinates import SkyCoord
from astropy.coordinates import FK5, FK4, AltAz, Galactic, CIRS
from astropy.coordinates import EarthLocation
from astropy.time import Time
import astropy.units as u
import astropy._erfa as erfa
import math
import time
import sys

__all__ = ["doppler_nanten"]

class doppler_nanten (object):

    #PATH_DEVICE_TABLE = "/home/amigos/NECST/soft/obs/params/device_table.prm"
    #doppler_1p85.py,motor_command.c,motor_server.c,nanten_astro.h,calc_doppler.cpp,
    dic1 = {"bandnum":2,
            #set sg_power [dBm]
            "power_sg21":13.0,
            "power_sg22":13.0,
            #light speed [km/sec]
            "LIGHT_SPEED":299792.458 }

    """
    dic1 = {"bandnum":2,
            #set frequency [GHz]
            "restFreq1":230.5380,
            "restFreq2":220.3986765,
            #12CO Rest frequency [GHz] from Koln Univ.
            "REST_FREQ_12COJ1_0":115.2712018,
            "REST_FREQ_12COJ2_1":230.5380000,
            "REST_FREQ_12COJ3_2":345.7959899,
            "REST_FREQ_12COJ4_3":461.0407682,
            "REST_FREQ_12COJ7_6":806.6518060,
            #13CO Rest frequency [GHz] from Koln Univ.
            "REST_FREQ_13COJ1_0":110.2013541,
            "REST_FREQ_13COJ2_1":220.3986190,
            "REST_FREQ_13COJ3_2":330.5878655,
            "REST_FREQ_13COJ4_3":440.7650398,
            "REST_FREQ_13COJ7_6":771.1838856,
            #C18O Rest frequency [GHz] from Koln Univ.
            "REST_FREQ_C18OJ1_0":109.7821734,
            "REST_FREQ_C18OJ2_1":219.5603541,
            "REST_FREQ_C18OJ3_2":329.3305525,
            "REST_FREQ_C18OJ4_3":439.0887658,
            "REST_FREQ_C18OJ7_6":768.2515933,
            #CI Rest frequency [GHz] from Koln Univ.
            "REST_FREQ_CI3P1_0":492.1606510,
            "REST_FREQ_CI3P2_1":809.3419700,
            #set speed [km/sec]
            #"vlsr":0,
            #Upper ***sb*:1 , Lower ***sb*:-1
            "1stsb1":1,
            "1stsb2":-1,
            #set frequency [GHz]
            "2ndLO1":8.038000000000,
            "2ndLO2":9.301318999999,

            #set sg_power [dBm]
            "power_sg21":13.0,
            "power_sg22":13.0,
            #light speed [km/sec]
            "LIGHT_SPEED":299792.458 }
    """

    coord_dict = {"equatorial" :"altaz",
                  "j2000"     : "fk5",
                  "b1950"     : "fk4",
                  "lb"        : "galactic",
                  "galactic"  : "galactic",
                  "gal"       : "galactic",
                  #"APPARENT"  : 10,
                  "HORIZONTAL": "altaz",
                  "same"      : 0}

    nanten2 = EarthLocation(lat = -22.96995611*u.deg, lon = -67.70308139*u.deg, height = 4863.85*u.m)
    
    def __init__(self):
        pass

    def get_vobs(self, mjdtmp, xtmp, ytmp, mode, offx, offy, dcos, offmode):
        mode = mode.lower()
        offmode = offmode.lower()
        mode = self.coord_dict[mode]
        offmode = self.coord_dict[offmode]
        on_coord = SkyCoord(xtmp, ytmp, unit="deg", frame=mode, obstime=self.t, location=self.nanten2)

        if offmode == "galactic":
            tmp = on_coord.transform_to(Galactic)            
        elif offmode == "altaz":
            tmp = on_coord.transform_to(AltAz)            
        elif offmode == "fk5":
            tmp = on_coord.transform_to(FK5)
        elif offmode == "fk4":
            tmp = on_coord.transform_to(FK4)
        elif offmode == "cirs":
            tmp = on_coord.transform_to(CIRS)            
        else:
            print("no coordinate")
            pass
        xxtmp = offx/3600. + tmp.data.lon.deg
        yytmp = offy/3600. + tmp.data.lat.deg
        calc_coord = SkyCoord(xxtmp, yytmp, unit="deg", frame=offmode, obstime=self.t,location=self.nanten2)
        radec_coord = calc_coord.transform_to(FK5)
        ra_tmp = math.radians(radec_coord.ra.deg)
        dec_tmp = math.radians(radec_coord.dec.deg)

        vobs = self.calc_vobs(ra_tmp, dec_tmp)
        print('vobs',vobs,type(vobs))

        return vobs

    def calc_vobs(self, ra_2000, dec_2000, unixtime):
        
        x_2000 = []
        x = []
        x_solar = []
        v_earth = []
        v_solar = []
        solar_tmp = []

        #1.85m at nobeyama
        #glongitude = 138.472153
        #nanten2 at atacama (nanten2wiki)
        glongitude = -67.70308139
        #1.85m at nobeyama
        #glatitude = 35.940874
        #nanten2 at atacama (nanten2wiki)
        glatitude = -22.96995611 
        #1.85m at nobeyama
        #gheight = 1386
        #nanten2 at atacama
        gheight = 4863.85

        #unixtime to astropy's Time object
        aTime = Time(dt.utcfromtimestamp(unixtime))
        #init
        a = math.cos(dec_2000)
        x_2000 = [a * math.cos(ra_2000), a * math.sin(ra_2000), math.sin(dec_2000)]

        tu = (aTime.jd - 2451545.) / 36525.
        #correction(precession, nutation)
        sc_fk5 = SkyCoord(ra = ra_2000*u.radian, dec = dec_2000*u.radian, frame = "fk5")
        trans = sc_fk5.transform_to(FK5(equinox = "J{}".format(2000.+tu*100.)))
        ranow = trans.ra.radian
        delnow = trans.dec.radian
        
        x = self.nutation(ranow, delnow, aTime)

        #Earth velocity to object
        earthloc = EarthLocation(lon = glongitude*u.deg, lat = glatitude*u.deg, height = gheight*u.m)
        earthloc_gcrs = earthloc.get_gcrs(aTime)
        sc_earth = SkyCoord(earthloc_gcrs).fk5

        v_earth = sc_earth.velocity.d_xyz.value

        vobs = - (v_earth[0] * x_2000[0] + v_earth[1] * x_2000[1] + v_earth[2] * x_2000[2])

        #solar
        sc_fk4_sol = SkyCoord(ra = 18*15*u.deg, dec = 30*u.deg, frame = "fk4")
        trans_sol = sc_fk4_sol.transform_to(FK5(equinox = "J{}".format(2000.+tu*100.)))
        rasol = trans_sol.ra.radian
        delsol = trans_sol.dec.radian
        
        solar_tmp = self.nutation(rasol, delsol, aTime)
        v_solar = [solar_tmp[0]*20, solar_tmp[1]*20, solar_tmp[2]*20]
        
        vobs = -(vobs - (v_solar[0] * x[0] + v_solar[1] * x[1] + v_solar[2] * x[2]))


        return vobs

    def nutation(self, ra, dec, aTime):
        
        pos = []

        a = math.cos(dec)
        tmp = [a * math.cos(ra), a * math.sin(ra), math.sin(dec)]
        
        #correction(nutation)
        ret = erfa.nut00a(aTime.jd, 0.0)
        nut_long = ret[0]
        nut_obliq = ret[1]
        
        pos.append(tmp[0] - (tmp[1] * math.cos(nut_obliq) + tmp[2] * math.sin(nut_obliq)) * nut_long)
        pos.append(tmp[1] + tmp[0] * math.cos(nut_obliq) * nut_long - tmp[2] * nut_obliq)
        pos.append(tmp[2] + tmp[0] * math.sin(nut_obliq) * nut_long + tmp[1] * nut_obliq)

        return pos

if __name__=="__main__":
    pass
