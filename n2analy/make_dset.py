import necstdb
import numpy
from tqdm import tqdm
import os
import xarray as xr

__all__ = ["get_data", "get_tpdata", "get_ac240data"]

def get_index(obsmode, scan_num, lamdel, betdel):
    mask1 = _obsmode == obsmode
    mask2 = _scan_number == scan_num
    mask3 = _lamdel == lamdel
    mask4 = _betdel == betdel
    mm1 = numpy.logical_and(mask3, mask4)
    #print(mm1)
    mm2 = numpy.logical_and(mask1, mask2)
    #print(mm2)
    mask5 = numpy.logical_and(mm1, mm2)
    return mask5#, mm1, mm2

def get_index2(obsmode, scan_num):
    mask1 = _obsmode == obsmode
    mask2 = _scan_number == scan_num
    mask3 = numpy.logical_and(mask1, mask2)
    return mask3

def get_tpdata(path, array_num):
    n = necstdb.opendb(path)
    nn = n.open_table("xffts_power_board{}".format(array_num))
    dd = n.open_table("obsmode")
    data = numpy.array(nn.read())
    obsmode = numpy.array(dd.read())
    print("read end")
    global _obsmode#?
    global _scan_number#?
    global _lamdel#?
    global _betdel#?
    _obs_timestamp =  numpy.array(list(map(lambda x:x.decode(), obsmode.T[0].tolist())))
    _obsmode = numpy.array(list(map(lambda x:x.decode().replace(" ", ""), obsmode.T[1].tolist())))
    _scan_number = numpy.array(list(map(lambda x:x.decode(), obsmode.T[2].tolist())))
    _lamdel =  numpy.array(list(map(lambda x:x.decode(), obsmode.T[3].tolist())))
    _betdel =  numpy.array(list(map(lambda x:x.decode(), obsmode.T[4].tolist())))
    array_timestamp = data.T[1].T
    ###
    obslist = numpy.unique(_obsmode).tolist()
    scanlist = numpy.unique(_scan_number)
    lamdel_list = numpy.unique(_lamdel)
    betdel_list = numpy.unique(_betdel)
    ###
    try:
        obslist.remove("Non")
    except:
        pass
    tmpobslist = []
    for j in tqdm(obslist):
        for k in scanlist:
            if j == "ON" or j == "OFF":
                for l in lamdel_list:
                    for m in betdel_list:
                        index = get_index(j, k, l, m)
                        try:
                            st2 = _obs_timestamp[index][0]
                            end2 = _obs_timestamp[index][-1]
                            tmpobslist.append([st2, end2, j, k, l, m])
                        except:
                            print(k,j,l,m)
            else:
                index = get_index2(j, k)
                try:
                    st2 = _obs_timestamp[index][0]
                    end2 = _obs_timestamp[index][-1]
                    tmpobslist.append([st2, end2, j, k, "", ""])
                except:
                    print(j,k)
    #return tmpobslist
    num = len(array_timestamp)
    a = [[0,0,0,0] for i in range(num)]
    for i in tmpobslist:
        #print(i)
        start = numpy.where(array_timestamp > float(i[0]))[0][0]
        end = numpy.where(array_timestamp < float(i[1]))[0][-1]
        #print(start, end)
        for j in range(start, end):
            #print(j)
            a[j][0] = i[2]
            a[j][1] = i[3]
            a[j][2] = i[4]
            a[j][3] = i[5]
    data = numpy.array(data)
    d = numpy.array(a)
    xffts_data = data.T[2].T
    obs_mode = d.T[0]
    scan_number = d.T[1]
    lamdel = d.T[2]
    betdel = d.T[3]
    xffts_timestamp = data.T[1].T
    freq = numpy.arange(32768)*2/32768
    cube = xr.DataArray(xffts_data, dims=["t"], coords={"t":xffts_timestamp,"obsmode":("t", obs_mode), "scannum":("t", scan_number), "x":("t", lamdel), "y":("t", betdel)})
    return cube

def get_data(path, array_num):
    n = necstdb.opendb(path)
    #print(n.list_tables())
    #nn = n.open_table(array_table)
    ### open file
    nn = n.open_table("xffts_board{}".format(array_num))
    #nn2 = n.open_table("xffts_power_board{}".format(array_num))
    dd = n.open_table("obsmode")
    ### read
    data = numpy.array(nn.read())
    #data2 = numpy.array(nn2.read())
    obsmode = numpy.array(dd.read())
    print("read end")
    ###抽出 obsmode
    global _obsmode
    global _scan_number
    global _lamdel
    global _betdel
    _obs_timestamp =  numpy.array(list(map(lambda x:x.decode(), obsmode.T[0].tolist())))
    _obsmode = numpy.array(list(map(lambda x:x.decode().replace(" ", ""), obsmode.T[1].tolist())))
    _scan_number = numpy.array(list(map(lambda x:x.decode(), obsmode.T[2].tolist())))
    _lamdel =  numpy.array(list(map(lambda x:x.decode(), obsmode.T[3].tolist())))
    _betdel =  numpy.array(list(map(lambda x:x.decode(), obsmode.T[4].tolist())))
    #_scan_number = obsmode.T[2]
    #_lamdel = obsmode.T[3]
    #_betdel = obsmode.T[4]
    array_timestamp = data.T[1].T
    ###共通の要素を削除
    obslist = numpy.unique(_obsmode).tolist()
    scanlist = numpy.unique(_scan_number)
    lamdel_list = numpy.unique(_lamdel)
    betdel_list = numpy.unique(_betdel)
    #print(lamdel_list)
    #print(betdel_list)
    try:
        obslist.remove("Non")
    except:
        pass
    tmpobslist = []
    for j in tqdm(obslist):
        for k in scanlist:
            if j == "ON" or j == "OFF":
                for l in lamdel_list:
                    for m in betdel_list:
                        index = get_index(j, k, l, m)
                        try:
                            st2 = _obs_timestamp[index][0]
                            end2 = _obs_timestamp[index][-1]
                            tmpobslist.append([st2, end2, j, k, l, m])
                        except:
                            print(k,j,l,m)
            else:
                index = get_index2(j, k)
                try:
                    st2 = _obs_timestamp[index][0]
                    end2 = _obs_timestamp[index][-1]
                    tmpobslist.append([st2, end2, j, k, "", ""])
                except:
                    print(j,k)
    #return tmpobslist
    num = len(array_timestamp)
    a = [[0,0,0,0] for i in range(num)]
    for i in tmpobslist:
        #print(i)
        start = numpy.where(array_timestamp > float(i[0]))[0][0]
        end = numpy.where(array_timestamp < float(i[1]))[0][-1]
        #print(start, end)
        for j in range(start, end):
            #print(j)
            a[j][0] = i[2]
            a[j][1] = i[3]
            a[j][2] = i[4]
            a[j][3] = i[5]
    #d, data, total_p
    data = numpy.array(data)
    d = numpy.array(a)
    xffts_data = data.T[2:].T
    obs_mode = d.T[0]
    scan_number = d.T[1]
    lamdel = d.T[2]
    betdel = d.T[3]
    xffts_timestamp = data.T[1].T
    freq = numpy.arange(32768)*2/32768
    cube = xr.DataArray(xffts_data, dims=["t", "GHz"], coords={"t":xffts_timestamp, "GHz":freq, "obsmode":("t", obs_mode), "scannum":("t", scan_number), "x":("t", lamdel), "y":("t", betdel)})
    return cube

def get_ac240data(path):
    n = necstdb.opendb(path)
    nn = n.open_table("ac240_spectra_data")
    dd = n.open_table("obsmode")
    ### read
    data = numpy.array(nn.read())
    obsmode = numpy.array(dd.read())
    print("read end")
    ###抽出 obsmode
    global _obsmode
    global _scan_number
    global _lamdel
    global _betdel
    _obs_timestamp =  numpy.array(list(map(lambda x:x.decode(), obsmode.T[0].tolist())))
    _obsmode = numpy.array(list(map(lambda x:x.decode().replace(" ", ""), obsmode.T[1].tolist())))
    _scan_number = numpy.array(list(map(lambda x:x.decode(), obsmode.T[2].tolist())))
    _lamdel =  numpy.array(list(map(lambda x:x.decode(), obsmode.T[3].tolist())))
    _betdel =  numpy.array(list(map(lambda x:x.decode(), obsmode.T[4].tolist())))
    array_timestamp = data.T[1].T
    ###共通の要素を削除
    obslist = numpy.unique(_obsmode).tolist()
    scanlist = numpy.unique(_scan_number)
    lamdel_list = numpy.unique(_lamdel)
    betdel_list = numpy.unique(_betdel)
    try:
        obslist.remove("Non")
    except:
        pass
    tmpobslist = []
    for j in tqdm(obslist):
        for k in scanlist:
            if j == "ON" or j == "OFF":
                for l in lamdel_list:
                    for m in betdel_list:
                        index = get_index(j, k, l, m)
                        try:
                            st2 = _obs_timestamp[index][0]
                            end2 = _obs_timestamp[index][-1]
                            tmpobslist.append([st2, end2, j, k, l, m])
                        except:
                            print(k,j,l,m)
            else:
                index = get_index2(j, k)
                try:
                    st2 = _obs_timestamp[index][0]
                    end2 = _obs_timestamp[index][-1]
                    tmpobslist.append([st2, end2, j, k, "", ""])
                except:
                    print(j,k)
    #return tmpobslist
    num = len(array_timestamp)
    a = [[0,0,0,0] for i in range(num)]
    for i in tmpobslist:
        #print(i)
        start = numpy.where(array_timestamp > float(i[0]))[0][0]
        end = numpy.where(array_timestamp < float(i[1]))[0][-1]
        #print(start, end)
        for j in range(start, end):
            #print(j)
            a[j][0] = i[2]
            a[j][1] = i[3]
            a[j][2] = i[4]
            a[j][3] = i[5]
    #d, data, total_p
    data = numpy.array(data)
    d = numpy.array(a)
    ac240_data = data.T[1:].T
    obs_mode = d.T[0]
    scan_number = d.T[1]
    lamdel = d.T[2]
    betdel = d.T[3]
    ac240_timestamp = data.T[0].T
    freq = numpy.arange(32768)*2/32768
    cube = xr.DataArray(ac240_data, dims=["t", "GHz"], coords={"t":ac240_timestamp, "GHz":freq, "obsmode":("t", obs_mode), "scannum":("t", scan_number), "x":("t", lamdel), "y":("t", betdel)})
    return cube
