import numpy as np
import h5py
class Antenna:
    """ antenna with location and timeseries of Efield"""
    def __init__(self,x,y,z,name=""):
        self.x = x
        self.y = y
        self.z = z
        self.name = name

class REvent:
    """ An interface class for reading simulations """
    def __init__(self,filename,parse_antenna=True):
        self.reasfile = filename
        if '.reas' in filename:
            self.reasfile = filename
            self.parse_reas(parse_antenna)
        elif '.hdf5' in filename:
            self.hdf5file = filename
            self.parse_hdf5()

    def parse_reas(self,parse_antenna):
        """ parse *reas file """
        f = open(self.reasfile)
        lines = f.readlines()
        for l in lines:
            if 'ShowerZenithAngle' in l:
                self.zenith = float(l.split()[2])
            if 'ShowerAzimuthAngle' in l:
                self.azimuth = float(l.split()[2]) + 180
                if self.azimuth > 360:
                    self.azimuth = self.azimuth - 360
            if 'DepthOfShowerMaximum' in l:
                self.xmax = float(l.split()[2])
            if 'PrimaryParticleEnergy' in l:
                self.energy = float(l.split()[2])/1e18
            if 'PrimaryParticleType' in l:
                self.part_id = int(l.split()[2])
            if 'MagneticFieldInclinationAngle' in l:
                self.Binc = float(l.split()[2])
            if 'MagneticFieldStrength' in l:
                self.Bmag = float(l.split()[2])
            if 'DistanceOfShowerMaximum' in l:
                self.dist_xmax = float(l.split()[2])/100 #m
        if parse_antenna == True:
            self.parse_reas_antenas()
        self.set_unit_vectors()

    def parse_reas_antenas(self):
        """Parse the antennas by reas """
        self.listfile = self.reasfile.replace('.reas','.list')
        f = open(self.listfile)
        lines = f.readlines()
        self.antennas = []
        print('reading ' +  str(len(lines)) + ' antennas')
        for l in lines:
            a = Antenna(float(l.split()[2])/100,float(l.split()[3])/100,float(l.split()[4])/100,l.split()[5])
            efile = self.listfile.replace('.list','_coreas/raw_'+ a.name + '.dat')
            a.t, a.Ex, a.Ey, a.Ez = np.loadtxt(efile,unpack=True)
            a.t = np.asarray(a.t)*1e9 #use nanoseconds
            a.Ex = np.asarray(a.Ex) * 2.99792458e10 #cgs statvolt/cm volt -> mu V/m (SI)
            a.Ey = np.asarray(a.Ey) * 2.99792458e10 #cgs statvolt/cm volt-> mu V/m (SI)
            a.Ez = np.asarray(a.Ez) * 2.99792458e10 #cgs statvolt/cm volt-> mu V/m (SI)
            self.antennas.append(a)

    def parse_hdf5(self):
        f = h5py.File(self.hdf5file, "r")
        self.antennas = []
        ai = f[list(f.keys())[-1] + '/AntennaInfo']
        for ai_ in ai:
            a = Antenna(ai_[1],ai_[2],ai_[3],ai_[0].decode('UTF-8'))
            self.antennas.append(a)
        print('reading ' +  str(len(self.antennas)) + ' antennas')

        traces = f[list(f.keys())[-1] + '/AntennaTraces']
        for tr in traces:
            for a in self.antennas:
                if a.name == tr:
                    break
            a.t = []
            a.Ex = []
            a.Ey = []
            a.Ez =[]
            for tup in traces[tr + '/efield']:
                a.t.append(tup[0])
                a.Ex.append(tup[1])
                a.Ey.append(tup[2])
                a.Ez.append(tup[3])
            a.t = np.asarray(a.t)
            a.Ex = np.asarray(a.Ex)
            a.Ey = np.asarray(a.Ey)
            a.Ez = np.asarray(a.Ez)

        ei = f[list(f.keys())[-1] + '/EventInfo']
        ei=ei[0]
        self.zenith = 180.-ei[4]
        self.azimuth = ei[5]+180
        if self.azimuth >= 360:
            self.azimuth -= 360
        self.xmax = ei[9]
        self.energy = ei[3]
        self.part_id = ei[2].decode('UTF-8')
        self.Bmag = ei[16]
        self.Binc = ei[17]
        self.Bdec = ei[18]
        self.ground=ei[11]
        self.dist_xmax=ei[6]
        self.set_unit_vectors()

    def set_unit_vectors(self):
        self.Bx = self.Bmag * np.cos(np.deg2rad(self.Binc))
        self.By = 0
        self.Bz = -self.Bmag * np.sin(np.deg2rad(self.Binc))
        self.uB = np.asarray([self.Bx/self.Bmag,self.By/self.Bmag,self.Bz/self.Bmag])
        ux = np.sin(np.deg2rad(self.zenith)) * np.cos(np.deg2rad(self.azimuth))
        uy = np.sin(np.deg2rad(self.zenith)) * np.sin(np.deg2rad(self.azimuth))
        uz = np.cos(np.deg2rad(self.zenith))
        self.uA = np.asarray([ux,uy,uz])
        self.uAxB = np.cross(self.uA,self.uB)
        self.uAxB = self.uAxB/(np.dot(self.uAxB,self.uAxB))**0.5
        self.uAxAxB = np.cross(self.uA,self.uAxB)
