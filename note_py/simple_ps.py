
# coding: utf-8

# In[43]:


import sys
if not sys.argv[1] == "-f":
    path = sys.argv[1]
    IF = "01"
    mode = "commandline"
else:
    # 手動で解析する場合はデータのあるpathを指定してください
    path = "/home/amigos/hdd/observation/simple_ps/20190918_130031"
    IF = "03"#XFFTSのboard番号　1-->"01"  12-->"12"
    mode = "notebook"


# In[44]:


import necstdb
import numpy
import matplotlib.pyplot as plt
import os
import pandas


# In[45]:


import sys
sys.path.append("/home/amigos/git/analy_n2data/script")


# In[46]:


import make_dset
#"04"は4IF目のこと。11IF目なら"11"
d, data = make_dset.get_data(path, IF)


# In[47]:


d = numpy.array(d)
data = numpy.array(data)


# In[48]:


xffts_data = data.T[2:].T


# In[49]:


obs_mode = d.T[0]


# In[50]:


hotmask = obs_mode == "HOT"
offmask = obs_mode == "OFF"
onmask = obs_mode == "ON"


# In[51]:


hot = numpy.mean(xffts_data[hotmask], axis=0)
off = numpy.mean(xffts_data[offmask], axis=0)
on = numpy.mean(xffts_data[onmask], axis=0)


# In[52]:


def chopper_wheel(on, off, hot, temprature = 300):
    Tastar = temprature * (on - off)/(hot - off)
    return Tastar


# In[53]:


T = chopper_wheel(on, off, hot)


# In[56]:


x = numpy.linspace(0, 2000, 32768)#XFFTS bw = 0-2000MHz
fig, ax = plt.subplots(1, 2, figsize=(14, 4))
ax[0].plot(x, T)
#ax[0].set_xlim(xmin, xmax)
#ax[0].set_ylim(ymin, ymax)
ax[0].grid(True)
ax[0].set_xlabel("MHz")
ax[0].set_ylabel("T [K]")
ax[0].set_title("Spectra Plot")

ax[1].plot(x, on, label="ON")
ax[1].plot(x, off, label="OFF")
ax[1].plot(x, hot, label="HOT")
# ax[1].set_xlim(-1500, -1200)
# ax[1].set_ylim(3000,10000)
ax[1].set_xlabel("MHz")
ax[1].set_ylabel("Count")
ax[1].grid(True)
ax[1].legend()
#ax[1].set_yscale("log")
ax[1].set_title("band chracter plot")

result_path = path.replace("data", "analysis")
if not os.path.exists(result_path):
    os.makedirs(result_path, exist_ok=True)
plt.savefig(os.path.join(result_path, "result_IF{}.png".format(IF)))
if mode == "notebook":
    plt.show()

