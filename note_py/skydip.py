
# coding: utf-8

# In[137]:


import sys
if not sys.argv[1] == "-f":
    analy_dir = sys.argv[1]
else:
    # 手動で解析する場合はデータのあるpathを指定してください
    analy_dir = "/home/amigos/data/skydip_xffts/20190907193057/"


# In[138]:


import n2df
import numpy
import matplotlib.pyplot as plt
import pandas
import os


# In[139]:


n = n2df.Read(analy_dir + "skydip.ndf")
if os.path.exists(analy_dir + "weather.csv"):
    w = pandas.read_csv(analy_dir + "weather.csv")
    temp = numpy.mean(w["cabin_temp1"])
    temp = temp + 273
else:
    print("[Warning] : weather.csv does not exist")
    print("[Warning] : use 300K as cabin temperature temporarily")
    temp = 300


# In[140]:


obs_mode = n.read_obs_mode()
data_list = []
for i in range(16):
    exec("data_list.append(n.read_onearray({}))".format(i))
El = n.read_scan_num()


# In[128]:


obs_mode = numpy.array(obs_mode)
El_list = numpy.array(El)


# In[129]:


hotmask = obs_mode == "HOT"
skymask = obs_mode == "SKY"
El = numpy.unique(El_list[skymask])


# In[130]:


data_list = numpy.array(data_list)
hot_list = []
for j in range(16):
    hot_list.append(numpy.mean(data_list[j][hotmask]))
print(El)
sky_list = []
for j in range(16):
    tmp = []
    for el in El:
        mask = El_list == el
        tmp.append(numpy.mean(data_list[j][mask]))
    sky_list.append(tmp)


# In[131]:


d_ = []
for j in range(16):
    tmp = []
    for i in range(len(El)):
        d_temp = hot_list[j] - sky_list[j][i]
        d_temp2 = numpy.log10(d_temp)
        tmp.append(d_temp2)
    d_.append(tmp)
    
# seczの計算
secz = []
for i in range(len(El)):
    secz_temp = (El[i]/180)*numpy.pi
    secz.append(1/numpy.cos(secz_temp))


# In[141]:


fig = plt.figure(figsize=(16,16))
ax = [fig.add_subplot(4, 4, i+1) for i in range(16)]
x = numpy.linspace(0, 2000, 32768)#XFFTS bw = 0-2000MHz
    
for i, _ax in enumerate(ax):
    f = numpy.polyfit(secz, d_[i], 1)
    _ax.plot(secz, d_[i], "o", label="sky")
    _ax.plot(secz, numpy.poly1d(f)(secz))
    _ax.set_xlabel('frequency [MHz]')
    _ax.set_ylabel("count")
    _ax.set_yscale("log")
    _ax.set_title('IF : {}'.format(i+1))
    _ax.text(0.1, 0.1, 'tau = {:.4f}'.format(f[0]), transform = _ax.transAxes)
    _ax.legend()
    _ax.grid()
    
plt.tight_layout()
plt.savefig(os.path.join(analy_dir, "result.png"))
plt.show()

