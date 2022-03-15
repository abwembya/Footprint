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
    def __init__(self,filename):
        self.reasfile = filename
        if '.reas' in filename:
            self.reasfile = filename
            self.parse_reas()
        elif '.hdf5' in filename:
            self.hdf5file = filename
            self.parse_hdf5()

    def parse_reas(self):
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
                self.Xmax = float(l.split()[2])
            if 'PrimaryParticleEnergy' in l:
                self.energy = float(l.split()[2])
            if 'PrimaryParticleType' in l:
                self.part_id = int(l.split()[2])
            if 'MagneticFieldInclinationAngle' in l:
                self.Binc = float(l.split()[2])
            if 'MagneticFieldStrength' in l:
                self.Bmag = float(l.split()[2])
        self.parse_reas_antenas()

    def parse_reas_antenas(self):
        """Parse the antennas by reas """
        self.listfile = self.reasfile.replace('.reas','.list')
        f = open(self.listfile)
        lines = f.readlines()
        self.antennas = []
        for l in lines:
            a = Antenna(float(l.split()[2]),float(l.split()[3]),float(l.split()[4]),l.split()[5])
            efile = self.listfile.replace('.list','_coreas/raw_'+ a.name + '.dat')
            a.t, a.Ex, a.Ey, a.Ez = np.loadtxt(efile,unpack=True)
            self.antennas.append(a)

    def parse_hdf5(self):
        f = h5py.File(self.hdf5file, "r")
        self.antennas = []
        ai = f[list(f.keys())[-1] + '/AntennaInfo']
        for ai_ in ai:
            a = Antenna(ai_[1],ai_[2],ai_[3],ai_[0].decode('UTF-8'))
            self.antennas.append(a)
        print('read ' +  str(len(self.antennas)) + ' antennas')

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

        ei = f[list(f.keys())[-1] + '/EventInfo']
        ei=ei[0]
        self.zenith = 180.-ei[4]
        self.azimuth = ei[5]
        self.xmax = ei[9]
        self.energy = ei[3]
        self.part_id = ei[2].decode('UTF-8')
        self.Bmag = ei[16]
        self.Binc = ei[17]
        self.Bdec = ei[18]
        self.ground=ei[11]
        self.dist_xmax=ei[6]
