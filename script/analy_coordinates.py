import numpy
import n2lite
import sqlite3
import matplotlib.pyplot as plt
import time
import n2df
from joblib import Parallel, delayed
import coordinate_calc
from datetime import datetime
from tqdm import tqdm

###
def log(log):
    now = datetime.now()
    print("{} : {}".format(now.strftime('%Y-%m-%d %H:%M:%S'),log))
st = time.time()

###path
path_to_encoder_db = "/home/amigos/ros/src/necst/scripts/record/otf_20190807_01_antenna_n31.db"
path_to_xfftsdb = "/home/amigos/ros/src/necst/scripts/record/hdd/otf20190807_n31.n2df"

#read from DB
n1 = n2lite.xffts_logger(path_to_encoder_db)
d1 = n1.read("encoder")
d1[0] = numpy.array(d1[0])

#reado from n2df file
n2 = n2df.Read(path_to_xfftsdb)
n2_timestamp = n2.read_timestamp()

log("read_end")

#azel -->radec
az = []
el = []
index = []

for i in range(len(n2_timestamp)):
    try:
        a = numpy.where(d1[0]>n2_timestamp[i])
        index.append(a[0][0])
    except Exception as e:
        print(i, e)

log("indexing end")

Az_list = numpy.array(d1[1])
diff_Az = Az_list[1:] - Az_list[:-1]
El_list = numpy.array(d1[2])
diff_El = El_list[1:] - El_list[:-1]
time_list = numpy.array(d1[0])
diff_time = time_list[1:] - time_list[:-1]

n_az = []
n_el = []
log("hokan")
for n,i in enumerate(index):
    try:
        n_az.append((diff_Az[i]/diff_time[i]) * (n2_timestamp[n] - time_list[i-1]) + Az_list[i-1])
        n_el.append((diff_El[i]/diff_time[i]) * (n2_timestamp[n] - time_list[i-1]) + El_list[i-1])
    except Exception as e:
        print(i)
        
n_t = []
for i in n2_timestamp:
    n_t.append(i)

n_t = n_t[:len(index)]

ret = coordinate_calc.fk5_from_altaz(numpy.array(n_az)/3600, numpy.array(n_el)/3600, n_t)
log("coordinate trans end")
ra = ret[0].deg
dec = ret[1].deg

log("coordinate calc start")
ret = coordinate_calc.fk5_from_altaz(Az_list/3600, El_list/3600, time_list)
log("coordinate calc end")

_ra = ret[0].deg
_dec = ret[1].deg

log("coordinate trans encoder end")

encoder = [_ra, _dec, time_list]
xffts_data = [ra,dec,n_t]
numpy.save("encoder_radec0807", encoder)
numpy.save("xffts_radec0807", xffts_data)

log("end {:.2f}".format(time.time()-st))
