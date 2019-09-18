
# coding: utf-8

# In[28]:


import sys
if not sys.argv[1] == "-f":
    path = sys.argv[1]
    mode = "commandline"
else:
    # 手動で解析する場合はデータのあるpathを指定してください
    path = "/home/amigos/hdd/data/observation/rsky/20190918_160218"
    mode = "notebook"


# In[29]:


import necstdb
import numpy
import matplotlib.pyplot as plt
import os
import pandas


# In[30]:


topicname = [
"xffts_board01",
"xffts_board02",
"xffts_board03",
"xffts_board04",
"xffts_board05",
"xffts_board06",
"xffts_board07",
"xffts_board08",
"xffts_board09",
"xffts_board10",
"xffts_board11",
"xffts_board12",
"xffts_board13",
"xffts_board14",
"xffts_board15",
"xffts_board16"
]


# In[31]:


def get_tsys(dhot, dsky, thot):
    y = dhot / dsky
    tsys = thot / (y - 1.)
    return tsys


# In[32]:


get_ipython().run_cell_magic('time', '', 'hot_list = []\nsky_list = []\ntsys_list = []\nfor i in topicname:\n    n = necstdb.opendb(path)\n    #print(n.list_tables())\n    nn = n.open_table("obsmode")\n    dd = n.open_table(i)\n    obsmode = numpy.array(nn.read())\n    spec_array = numpy.array(dd.read())\n\n    timestamp = obsmode[:,0]\n    obsmode2 = list(map(lambda x:x.decode(), obsmode[:,1].tolist()))\n\n    obsmode2 = numpy.array(obsmode2)\n    hotmask = obsmode2 == "HOT"\n    skymask = obsmode2 == "SKY"\n\n    array = spec_array.T[2:].T\n    array_timestamp = spec_array.T[1].T\n\n    start_time = timestamp[hotmask][0]\n    end_time = timestamp[hotmask][-1]\n\n    start_time2 = timestamp[skymask][0]\n    end_time2 = timestamp[skymask][-1]\n\n    print(array_timestamp[0])\n    st_index = numpy.where(array_timestamp > float(start_time))[0][0]#分光データのtimstampから切り出す部分の始め\n    end_index = numpy.where(array_timestamp < float(end_time))[0][-1]# 終わり\n    st_index2 = numpy.where(array_timestamp > float(start_time2))[0][0]#分光データのtimstampから切り出す部分の始め\n    end_index2 = numpy.where(array_timestamp < float(end_time2))[0][-1]# 終わり\n\n    tm = array[st_index:end_index]#要注意\u3000切り出しデータ\n    hot = numpy.mean(tm, axis=0)\n    tm2 = array[st_index2:end_index2]#要注意\u3000切り出しデータ\n    sky = numpy.mean(tm2, axis=0)\n    hot_list.append(hot)\n    sky_list.append(sky)\n    tsys_list.append(get_tsys(hot, sky, 300))')


# In[33]:


fig = plt.figure(figsize=(16,16))
ax = [fig.add_subplot(4, 4, i+1) for i in range(16)]
x = numpy.linspace(0, 2000, 32768)#XFFTS bw = 0-2000MHz
    
# plot hot
for i, (_ax, _tsys) in enumerate(zip(ax, tsys_list)):
    _ax.plot(x, hot_list[i], "r-", label="hot")
    _ax.plot(x, sky_list[i], "b-", label="sky")
    _ax0 = _ax.twinx()
    _ax0.plot(x, tsys_list[i], "g.", label="Tsys", alpha=0.1)
    _ax.set_xlabel('frequency [MHz]')
    _ax.set_ylabel("count")
    _ax.set_yscale("log")
    _ax0.set_ylabel('Tsys [K]')
    _ax.set_title('IF : {}'.format(i+1))
    tsys_av = numpy.mean(_tsys)
    _ax.text(0.05, 0.05, 'Tsys = %.2f'%(tsys_av), transform=_ax0.transAxes)
    _ax0.set_ylim(0, 600)
    _ax.legend()
    _ax.grid()


# In[34]:


plt.tight_layout()
result_path = path.replace("data", "analysis")
if not os.path.exists(result_path):
    os.makedirs(result_path, exist_ok=True)
plt.savefig(os.path.join(result_path, "result_rsky.png"))
if mode == "notebook":
    plt.show()

