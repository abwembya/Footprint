from earsim import REvent
import scipy
import os
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import sys
#input path of the hdf5 set



#Input files list
fileNames = sys.argv[2:]
if len(fileNames) == 0:
    fileNames.append('/home/anthony/Documents/Stshp_Iron_0.0251_71.6_0.0_9.hdf5')

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
        j=bandPassFilter(ev.antennas[i].Ex,1/dt)
        k=bandPassFilter(ev.antennas[i].Ey,1/dt)
        if (any(a >lim for a in k)or any(a >lim for a in j)) == True:
            yp.append(y[i])
            xp.append(x[i])
            footprt=np.append(footprt,i)
            footprt
        else:
            None
    if len(xp)>1:#if the array has atleas two points calculate area
        Area1= np.pi*max(map(abs, xp))*max(map(abs, yp))
        u=0     #x-position of the center
        v=0  #y-position of the center
        a=max(map(abs, xp))    #radius on the x-axis
        b=max(map(abs, yp))   #radius on the y-axis
        xx=min(map(abs,xp))
        yy=min(map(abs,yp))
        xV=[]
        yV=[]
        c=0
        d=0
        for i in range(len(yp)):
            if yp[i]== 0:
                xV.append(xp[i])
                c=min(map(abs, xV))
                if a==c:
                    c=a*0.95
            else:
                iy=list(map(abs, yp)).index(yy)
                c=xp[iy]

        for i in range(len(yp)):
            if xp[i]== 0:
                yV.append(xp[i])
                d=min(map(abs, yV))
                if b==d:
                    d=b*0.95
            else:
                ix=list(map(abs,xp)).index(abs(xx))
                d=yp[ix]

        Area2= np.pi*abs(c)*abs(d)
        Area=Area1-Area2
        t = np.linspace(0, 2*np.pi, 100)
        #plt.scatter(xp,yp)
        #plt.xlabel('x [m]')
        #plt.ylabel('y [m]')
        #plt.plot( u+a*np.cos(t) , v+b*np.sin(t),label=str(lim)+' $\mu V/m$ outter')
        #plt.plot( u+c*np.cos(t) , v+d*np.sin(t),label=str(lim)+' $\mu V/m$ inner' )
        #plt.legend(title="footprint", fontsize=10, title_fontsize=15)
        #plt.grid()
        #plt.show()
        #print(str(lim)+ r' micro V/m = '+str(round(Area,2))+r'$m^2$' )
        return round(Area,4),round(a,2),round(b,2)
    else:
        #print('No detection at  '+str(lim)+' micro V')
        return 0,0,0
#headers
ss=[u'\u0023 part_id',u'\u0023 Energy',u'\u0023 xmax ',u'\u0023 Zenith' , u'\u0023 Azimuth',u'\u0023  A_25 ',u'\u0023  A_50',u'\u0023 A_75',u'\u0023 A_100',u'\u0023  A_200',u'\u0023  Id',u'\u0023  EeV',u'\u0023  g/cm', u'\u0023  deg', u'\u0023  deg',u'\u0023  m^2',u'\u0023  m^2',u'\u0023 m^2',u'\u0023  m^2', u'\u0023 m^2']


'''reading multiple files and calculating the area/ nb/ best turn imageing of in function'''

#file_list = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path,f)) and f.endswith('.hdf5')]
A51 = np.array([])
A51=np.append(A51, ss ,axis=0)
for i in range(len(fileNames)):
    try:
        fname = (fileNames[i])
        ev = REvent(fname)
    except KeyError:
        pass
    x = np.asanyarray([a.x for a in ev.antennas])
    y = np.asanyarray([a.y for a in ev.antennas])
    limz=[25,50,75,100,200]
    flim0=footprint(limz[0])
    flim1=footprint(limz[1])
    flim2=footprint(limz[2])
    flim3=footprint(limz[3])
    flim4=footprint(limz[4])
    A51=np.append(A51, [ ev.part_id,ev.energy,ev.xmax,ev.zenith,ev.azimuth,flim0[0],flim1[0],flim2[0],flim3[0],flim4[0]],axis=0)
#total number of files processed
print('number of files processed: ',len(fileNames))

#output processing in to rows and columns
#OUTPUT/dat/csv/txt///
if len(sys.argv) < 2:
    output="footprt_"+str(A51.size/10)+".txt"
else:
    output = sys.argv[1]


A51=np.reshape(A51, (-1,10))
np.savetxt(output, A51,delimiter = ",",fmt='%s')
#outputfill can be
append_copy = open(output, "r")
original_text = append_copy.read()
append_copy.close()

#verion number
append_copy = open(output, "w")
s=u"\u0023 Copyright -- Anthony-- 2022_v3\n"
append_copy.write(s)
append_copy.write(original_text)
append_copy.close()
#Enddddddd
