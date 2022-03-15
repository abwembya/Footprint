from earsim import REvent
import scipy
import os
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import sys
#input path of the hdf5 set

if len(sys.argv) < 2:
    path='/home/anthony/Documents/'
else:
    path= sys.argv[2]


def bandPassFilter(signal,fs,lowcut=0.03, hicut=0.08, order = 6):#GHz
    '''Returns filtered signal using thr butter worth filter of order 6'''
    niq=fs/2
    low= lowcut/niq
    high=hicut/niq

    b,a=scipy.signal.butter(order,[low,high],'bandpass',analog=False)
    y = scipy.signal.filtfilt(b,a,signal)
    return (y)



def footprint(lim=100):
    '''Calculting the area of the radio footptint of the shower '''
    footprt=np.array([])
    yp=[]
    xp=[]
    dt = ev.antennas[0].t[1]-ev.antennas[0].t[0]
    for i in range(len(ev.antennas)):
        j=bandPassFilter(ev.antennas[i].Ex,dt,)
        k=bandPassFilter(ev.antennas[i].Ey,dt,)
        if (any(a >lim for a in k)or any(a >lim for a in j)) == True:
            yp.append(y[i])
            xp.append(x[i])
            footprt=np.append(footprt,i)
            footprt
        else:
            None
    if len(xp)>1:#if the array has atleas two points calculate area
        Area= np.pi*max(map(abs, xp))*max(map(abs, yp))
        u=0     #x-position of the center
        v=0  #y-position of the center
        a=max(map(abs, xp))    #radius on the x-axis
        b=max(map(abs, yp))   #radius on the y-axis
        #t = np.linspace(0, 2*np.pi, 100)
        #plt.scatter(xp,yp)
        #plt.xlabel('x [m]')
        #plt.ylabel('y [m]')
        #plt.plot( u+a*np.cos(t) , v+b*np.sin(t),label=str(lim)+' $\mu V/m$' )
        #plt.grid(color='lightgray',linestyle='--')
        #plt.legend(title="footprint ="+str(round(Area,2)), fontsize=10, title_fontsize=15)
        #plt.grid()
        #plt.show()
        #print(str(lim)+ r' micro V/m = '+str(round(Area,2))+r'$m^2$' )
        return round(Area,4),round(a,2),round(b,2)
    else:
        #print('No detection at  '+str(lim)+' micro V')
        return 0,0,0

'''reading multiple files and calculating the area/ nb/ best turn imageing of in function'''
#path='/home/anthony/Documents/'
file_list = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path,f)) and f.endswith('.hdf5')]
A51 = np.array([])
for i in range(len(file_list)):
#for i in range(0,4):
      fname = file_list[i]
      ev = REvent(path+fname)
      x = np.asanyarray([a.x for a in ev.antennas])
      y = np.asanyarray([a.y for a in ev.antennas])
      limz=[25,50,75,100,200]
      flim0=footprint(limz[0])
      flim1=footprint(limz[1])
      flim2=footprint(limz[2])
      flim3=footprint(limz[3])
      flim4=footprint(limz[4])
      A51=np.append(A51, [ ev.energy,ev.xmax,ev.zenith,ev.azimuth,flim0[0],flim0[1],flim0[2],flim1[0],flim1[1],flim1[2],flim2[0],flim2[1],flim2[2],flim3[0],flim3[1],flim3[2],flim4[0],flim4[1],flim4[2] ],axis=0)
#print(file_list)

A51=np.reshape(A51, (-1,19))

output = sys.argv[1]
if len(output) == 0:
    output.append("footprt_"+str(A51.size/19)+".txt")

np.savetxt(output, A51,delimiter = ",")
append_copy = open(output, "r")
original_text = append_copy.read()
append_copy.close()

#sadding headers of columns
append_copy = open(output, "w")
s=u"""\u0023 Copyright -- Anthony-- 2022_v01\n,\u0023 Energy,\u0023 2 xmax  ,\u0023 3 zenith , \u0023 4 azimuth,\u0023 5 Area(25 micro V/m) ,\
\u0023 6 x_max(25),\u0023 7 y_max(25),\u0023 8 Area(50 micro V/m),\u0023 9 x_max(50) ,\u0023 10 y_max(50),\u0023 11 Area(75 microV/m),\u0023 12 x_max(75), \u0023 13 y_max(75),\u0023 14 Area(100microV/m),\u0023 15 x_max(100) ,\u0023 16 y_max(100), \u0023 17 Area(200 micro/V) \u0023 18 x_max(200) , \u0023 19 y_max(200)"""
ss="""\n \u0023 1 EeV,\u0023 2 g/cm ,\u0023 3 deg, \u0023 4 deg,\u0023 5 m^2,\u0023 6 m ,\u0023 7 m,\u0023 8 m^2,\u0023 9 m ,\u0023 m,\u0023 11 m^2,\u0023 m , \u0023 13 m,\
\u0023 14 m^2,\u0023 15m ,\u0023 16 m, \u0023 17 m^2, \u0023 18 m , \u0023 m"""
append_copy.write(s+ss)

append_copy.write(original_text)
append_copy.close()
