import numpy as np
import os,sys,shutil
import numpy.ma as ma
import datetime
import csv
import matplotlib.pyplot as plt
import linecache
import time
import arcpy
arcpy.CheckOutExtension("Spatial")
from datetime import datetime,timedelta
from dateutil import parser

class Estimation():
    def __init__(self,datax,datay,dataz):
        self.x=datax
        self.y=datay
        self.v=dataz

    def estimate(self,x,y,using='ISD'):
        if using=='ISD':
            return self._isd(x,y)

    def _isd(self,x,y):
        d=np.sqrt((x-self.x)**2+(y-self.y)**2)
        if d.min () >0:
            v=np.sum(self.v*(1/d**2)/np.sum(1/d**2))
            return v

        else:
            return self.v[d.argmin()]

def readASCI(fileName):
        line=[]
        for i in range(1,7):
            line.append(linecache.getline(fileName,i))

        ncol=int(line[0].split()[1])
        print ncol
        nrow=int(line[1].split()[1])
        xl=float(line[2].split()[1])
        yl=float(line[3].split()[1])
        print xl,yl
        cell_size=float(line[4].split()[1])
        no_data=float(line[5].split()[1])
        print fileName,ncol,nrow,no_data
        #data=np.genfromtxt(fileName,skiprows=6)
        #data_new=np.around(data,decimals=5)
        return ncol,nrow,xl,yl,cell_size


def simple_idw(x, y, z, xi, yi):
    dist = distance_matrix(x,y, xi,yi)

    # In IDW, weights are 1 / distance
    weights = 1.0 / dist

    # Make weights sum to one
    weights /= weights.sum(axis=0)

    # Multiply the weights for each interpolated point by all observed Z-values
    zi = np.dot(weights.T, z)
    return zi


def linear_rbf(x, y, z, xi, yi):
    dist = distance_matrix(x,y, xi,yi)

    # Mutual pariwise distances between observations
    internal_dist = distance_matrix(x,y, x,y)

    # Now solve for the weights such that mistfit at the observations is minimized
    weights = np.linalg.solve(internal_dist, z)

    # Multiply the weights for each interpolated point by the distances
    zi =  np.dot(dist.T, weights)
    return zi

def scipy_idw(x, y, z, xi, yi):
    interp = Rbf(x, y, z, function='linear')
    return interp(xi, yi)


def distance_matrix(x0, y0, x1, y1):
    obs = np.vstack((x0, y0)).T
    interp = np.vstack((x1, y1)).T
    # Make a distance matrix between pairwise observations
    # Note: from <http://stackoverflow.com/questions/1871536>
    # (Yay for ufuncs!)
    d0 = np.subtract.outer(obs[:,0], interp[:,0])
    d1 = np.subtract.outer(obs[:,1], interp[:,1])
    return np.hypot(d0, d1)


def CreateFolder(folderName):
    if os.path.isdir(folderName)==True:
        shutil.rmtree(folderName)
        os.mkdir(folderName)
    else:
        os.mkdir(folderName)


def pathSaved(location):
    new_string=location.split('\\')
    f_location=''
    for x in range(0,len(new_string)-1):
        f_location=f_location+str(new_string[x])+"\\"
    return f_location



mxd=arcpy.mapping.MapDocument("CURRENT")
WorkDir=pathSaved(mxd.filePath)
os.chdir(WorkDir)
CreateFolder('Observed')
os.chdir(os.path.join(WorkDir,'Observed'))

csv_file=arcpy.GetParameterAsText(0)
start_date=arcpy.GetParameterAsText(1)
end_date=arcpy.GetParameterAsText(2)
frequency=arcpy.GetParameterAsText(3)
boundary_input=arcpy.GetParameterAsText(4)

st_date=parser.parse(start_date)
en_date=parser.parse(end_date)

arcpy.ProjectRaster_management(boundary_input,'wgs_boundary',arcpy.SpatialReference('WGS 1984'))
left_X=float(arcpy.GetRasterProperties_management('wgs_boundary','LEFT').getOutput(0))
right_X=float(arcpy.GetRasterProperties_management('wgs_boundary','RIGHT').getOutput(0))
bottom_y=float(arcpy.GetRasterProperties_management('wgs_boundary','BOTTOM').getOutput(0))
top_y=float(arcpy.GetRasterProperties_management('wgs_boundary','TOP').getOutput(0))
cell_size=float(arcpy.GetRasterProperties_management('wgs_boundary','CELLSIZEX').getOutput(0))
rows=int(arcpy.GetRasterProperties_management(boundary_input,'ROWCOUNT').getOutput(0))
cols=int(arcpy.GetRasterProperties_management(boundary_input,'COLUMNCOUNT').getOutput(0))
bbox=[xl,yl,right_X,top_y]



coord=[]
data=[]

## read csv files for Lat and Long and check for the missing data
with open(csv_file) as f:
    r=csv.reader(f)

    for i,row in enumerate(r):
        if i in range(1,3):
            coord.append(map(float,row[1:]))

        elif i>2:
            data.append(row[0:])

        else:
            pass

obs_start_dt=parser.parse(data[0][0])
obs_end_dt=parser.parse(data[-1][0])


if frequency=='Daily':
    obs=[np.datetime64(obs_start_dt)+np.timedelta64(tt,'D') for tt in range(len(data))]
    sel=[np.datetime64(st_date)+np.timedelta64(xx,'D') for xx in range(0,(en_date-st_date).days+1)]
    select_date=[st_date + timedelta(tt) for tt in range((en_date - st_date).days + 1)]

elif frequency=='Hourly':
    diff=(en_date-st_date)
    obs=[np.datetime64(obs_start_dt)+np.timedelta64(tt,'h') for tt in range(len(data))]
    sel=[np.datetime64(st_date)+np.timedelta64(xx,'h') for xx in range(0,(diff.days*24+diff.seconds/3600)+1)]
    select_date=[st_date + timedelta(hours=tt) for tt in range((diff.days*24+diff.seconds/3600)+1)]


select_data=[]
for i in range(len(data)):
    if obs[i]<sel[0] or obs[i]>sel[-1]:
        continue

    select_data.append(data[i][1:])


lon=np.array(coord[0])
lat=np.array(coord[1])
data_array=np.array(select_data,dtype='float32')
data_mask_array=ma.masked_values(data_array,-9999)


xll=[xl]
yll=[yl]

for i in range(cols-1):
    yl=yl+cell_size
    yll.append(yl)

for j in range(rows-1):
    xl=xl+cell_size
    xll.append(xl)


xll=np.array(xll)
yll=np.array(yll)

xi,yi=np.meshgrid(xll,yll)
xi,yi=xi.flatten(),yi.flatten()


f=open('Observed_rainfall.BIN','wb+')

for j in range(0,len(select_data)):
    arcpy.gp.addMessage(select_date[j])

    if data_mask_array[j].mask.all()==True:
        grid=np.zeros((rows,cols))

    else:

        x=data_mask_array[j].mask
        ind=np.where(x==0)
        data_use=data_mask_array[j][ind]
        select_lon=lon[ind]
        select_lat=lat[ind]
        grid1=simple_idw(select_lon,select_lat,data_use,xi,yi)
        grid1=grid1.reshape((cols,rows))
        grid=np.flipud(grid1)

    grid_to_fortran=np.asfortranarray(grid,'float32')
    grid_to_fortran.tofile(f)
    np.savetxt('file_'+str(j)+'.txt',grid)

f.close()
arcpy.Delete_management('wgs_boundary')
