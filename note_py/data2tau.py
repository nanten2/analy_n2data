#coding UTF-8
import numpy as np
import astropy.io as fits
import math
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import sys
sys.path.append('/home/amigos/git/analy_n2data')
import n2analy

class analy_skydip:

    def __init__(self):

        path = ('/home/amigos/nfs_hdd3/data/observation/skydip_xffts/20191227020251')
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

        self.all_list = [data_1, data_2, data_3, data_4, data_5, data_6, data_7, data_8, data_9, data_10, data_11, data_12, data_13, data_14, data_15, data_16]
        self.path = path
        self.obsmode_separation()
        self.get_total_power()
        self.get_hot_sky()
        self.calc_secz()
        self.poly_fit()
        self.plot()


    def obsmode_separation(self):
        sky_list = []
        hot_list = []

        for i in self.all_list:
            skymask = i['obsmode'] == 'SKY'
            hotmask = i['obsmode'] == 'HOT'
            sky_list.append(np.array(i)[skymask])
            hot_list.append(np.array(i)[hotmask])

            self.sky_list = sky_list
            self.hot_list = hot_list
        
    def get_total_power(self):
        tp_list = []

        for i in self.all_list:
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
        self.tp_list = tp_list

    def get_hot_sky(self):
        hot_list_mean = []
        for i in self.hot_list:
            hot_list_mean.append(np.mean(np.array(i)))
        
        d_hot_sky = []
        d_hot_sky_tempo = []

        self.tp_list = np.array(self.tp_list)
        #print(tp_list.shape)

        for j in range(len(self.tp_list)):
            d_hot_sky1=[]
            hot_list_mean_ = hot_list_mean[j]
            for i in self.tp_list[j]:
                #print(i)
                #print(hot_list_mean)
                #print(i)
                d_temp = hot_list_mean_ - i
                print(d_temp)
                #print(d_temp)
                try:
                    d_temp2 = math.log(d_temp)
                except:
                    d_temp2 = 0
                    print('Including bad data')
                d_hot_sky1.append(d_temp2)
            d_hot_sky.append(d_hot_sky1)

            self.d_hot_sky = d_hot_sky

    def calc_secz(self):
        z = [80, 70, 60, 45, 30, 25, 20]
        _z = []
        for i in range(len(z)):
            __z = 90 - z[i]
            _z.append(__z)

        secz = []
        for i in range(len(_z)):
            secz_temp = (_z[i]/180)*math.pi
            secz.append(1/math.cos(secz_temp))

        _secz = sorted(secz, reverse=False)
                        
        self._secz = _secz
        self.secz = secz
    
    def poly_fit(self):
        fit_array_list =[]

        for i in self.d_hot_sky:
            try:
                fit = np.polyfit(self.secz, np.array(i),1)
                fit_array_list.append(fit)
            except:
                fit_array_list.append(np.zeros(2))
                print('fuck')

        self.fit_array_list = fit_array_list

    def plot(self):

        fit_array_list = self.fit_array_list
        secz = self.secz
        d_hot_sky = self.d_hot_sky
      

        fig = plt.figure(figsize=(16,16))
        fig.suptitle(self.path, fontsize=20)

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
        plt.subplots_adjust(top=0.93)
        plt.savefig('12_27_skydip.png')
        plt.show()
        
        

if __name__ == '__main__':
    t=analy_skydip()