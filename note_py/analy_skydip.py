
# coding: utf-8

# In[1]:
import sys
if not sys.argv[1] == "-f":
    path = sys.argv[1]
    mode = "commandline"
else:
    path = "/home/amigos/hdd/data/observation/rsky/20191113_032816"#例
    mode = "notebook
"
#get_ipython().magic('matplotlib inline')
import numpy as np
import astropy.io as fits
import math
import matplotlib as mpl
import matplotlib.pylab as plt
from scipy.optimize import curve_fit

sys.path.append('/home/amigos/git/analy_n2data')


# In[2]:

import n2analy


# In[ ]:

data_1 = n2analy.get_tpdata(path, '01')
data_2 = n2analy.get_tpdata(path, '02')
data_3 = n2analy.get_tpdata(path, '03')
data_4 = n2analy.get_tpdata(path, '04')
data_5 = n2analy.get_tpdata(path, '05')
data_6 = n2analy.get_tpdata(path, '06')
data_7 = n2analy.get_tpdata(path, '07')
data_8 = n2analy.get_tpdata(path, '08')
data_9 = n2analy.get_tpdata(path, '09')
data_10 = n2analy.get_tpdata(path, '10')
data_11 = n2analy.get_tpdata(path, '11')
data_12 = n2analy.get_tpdata(path, '12')
data_13 = n2analy.get_tpdata(path, '13')
data_14 = n2analy.get_tpdata(path, '14')
data_15 = n2analy.get_tpdata(path, '15')
data_16 = n2analy.get_tpdata(path, '16')


# In[4]:

data_list = [data_1, data_2, data_3, data_4, data_5, data_6, data_7, data_8, data_9, data_10, data_11, data_12, data_13, data_14, data_15, data_16]


# In[5]:

print(np.array(data_list[0]))


# In[ ]:




# In[6]:

#classify obsmode
data_list2 = []
hot_list = []

for i in data_list:
    skymask = i['obsmode'] == 'SKY'
    hotmask = i['obsmode'] == 'HOT'
    data_list2.append(np.array(i)[skymask])
    hot_list.append(np.array(i)[hotmask])
    
print(np.array(hot_list).shape)


# In[7]:

tp_list = []

for i in data_list:
    sequence1 = []
    el_80_mask = i['scannum'] == '80.0'
    el_70_mask = i['scannum'] == '70.0'
    el_60_mask = i['scannum'] == '60.0'
    el_45_mask = i['scannum'] == '45.0'
    el_30_mask = i['scannum'] == '30.0'
    el_25_mask = i['scannum'] == '25.0'
    el_20_mask = i['scannum'] == '20.0'
    
    sequence1.append(np.mean(np.array(i[el_80_mask])))
    sequence1.append(np.mean(np.array(i[el_70_mask])))
    sequence1.append(np.mean(np.array(i[el_60_mask])))
    sequence1.append(np.mean(np.array(i[el_45_mask])))
    sequence1.append(np.mean(np.array(i[el_30_mask])))
    sequence1.append(np.mean(np.array(i[el_25_mask])))
    sequence1.append(np.mean(np.array(i[el_20_mask])))
    
    tp_list.append(sequence1)


# In[8]:

np.array(tp_list).shape


# In[9]:

# calc tau
#log(p_hot-p_sky)のlistの作成   

hot_list_mean = []
for i in hot_list:
    hot_list_mean.append(np.mean(np.array(i)))
    
print(np.array(hot_list_mean).shape)

print(np.array(tp_list).shape)


# In[10]:

d_hot_sky = []
d_hot_sky_tempo = []

tp_list = np.array(tp_list)


for j in range(len(tp_list)):
    d_hot_sky1=[]
    hot_list_mean_ = hot_list_mean[j]
    for i in tp_list[j]:
        #print(i)
        #print(hot_list_mean)
        #print(i)
        d_temp = hot_list_mean_ - i
        #print(d_temp)
        #print(d_temp)
        try:
            d_temp2 = math.log(d_temp)
        except:
            d_temp2 = 0
        d_hot_sky1.append(d_temp2)
    d_hot_sky.append(d_hot_sky1)


# In[11]:

np.array(d_hot_sky).shape


# In[12]:

#seczの計算  
z = [80, 70, 60, 45, 30, 25, 20]
_z = []
for i in range(len(z)):
    __z = 90 - z[i]
    _z.append(__z)

secz = []
for i in range(len(_z)):
    secz_temp = (_z[i]/180)*math.pi
    secz.append(1/math.cos(secz_temp))

#print(d_hot_sky1)
#print(d_hot_sky2)

#print(secz)

_secz = sorted(secz, reverse=False)
#print(secz)
import matplotlib.pyplot as plt2
#fig = plt2.figure(figsize=(20.0, 6.0))
#ax = fig.add_subplot(111)
#ax.plot(d_hot_sky1)
#plt2.plot(secz, d_hot_sky[0])
#plt2.plot(secz, d_hot_sky[1])
#plt2.show

print(np.array(d_hot_sky).shape)


# In[ ]:




# In[13]:

fit_array_list =[]

for i in d_hot_sky:
    try:
        fit = np.polyfit(secz, np.array(i),1)
        fit_array_list.append(fit)
    except:
        fit_array_list.append(np.zeros(2))
    
#print(np.array(fit_array_list[1][0][1]))


fit_array_list_debug=[]


        


# In[14]:

fig = plt.figure(figsize=(16,16))
ax = [fig.add_subplot(4, 4, i+1) for i in range(16)]
    
for i, _ax in enumerate(ax):
    if (-1*fit_array_list[i][0] >= 1) or (-1*fit_array_list[i][0] <= 0):
        _ax.text(0.3, 0.5, 'bad data', transform = _ax.transAxes, fontsize=25)
    else:
        try:
            _ax.plot(secz, np.poly1d(fit_array_list[i])(secz))
            _ax.plot(secz, d_hot_sky[i], 'o')
            _ax.text(0.1, 0.1, 'tau = {:.4f}'.format(-1*fit_array_list[i][0]), transform = _ax.transAxes)
        except:
            _ax.text(0.3, 0.5, 'bad data', transform = _ax.transAxes, fontsize=25)

    _ax.set_xlabel('secZ')
    _ax.set_ylabel("count")
    _ax.set_yscale("log")
    _ax.set_title('IF : {}'.format(i+1))
    _ax.legend()
    _ax.grid()
    
plt.tight_layout()

if mode == "commandline":
    result_name = os.path.dir(path)
    plt.savefig("/home/amigos/result/skydip/{}.png".format(result_name))
else:
    plt.show()
# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




#



# In[ ]:




# In[ ]:




# In[ ]:



