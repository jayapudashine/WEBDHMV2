#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Jaya
#
# Created:     19/06/2016
# Copyright:   (c) Jaya 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import netCDF4 as netcdf
import numpy as np
import os,shutil
from datetime import timedelta
import arcpy
from datetime import datetime
import pydap.client
import scipy.interpolate

def spatialSubset(lat, lon, res, bbox):
    """Subsets arrays of latitude/longitude based on bounding box *bbox*."""
    if bbox is None:
        i1 = 0
        i2 = len(lat)-1
        j1 = 0
        j2 = len(lat)-1
    else:
        i1 = np.where(bbox[3] <= lat+res/2)[0][-1]
        i2 = np.where(bbox[1] >= lat-res/2)[0][0]
        j1 = np.where(bbox[0] >= lon-res/2)[0][-1]
        j2 = np.where(bbox[2] <= lon+res/2)[0][0]
    return i1, i2+1, j1, j2+1



def CreateFolder(folderName):

    if os.path.isdir(folderName)==True:
        shutil.rmtree(folderName)
        os.mkdir(folderName)
    else:
        os.mkdir(folderName)


def simple_idw(x, y, z, xi, yi):
    dist = distance_matrix(x,y, xi,yi)

    # In IDW, weights are 1 / distance
    weights = 1.0 / dist

    # Make weights sum to one
    weights /= weights.sum(axis=0)

    # Multiply the weights for each interpolated point by all observed Z-values
    zi = np.dot(weights.T, z)
    return zi

def distance_matrix(x0, y0, x1, y1):
    obs = np.vstack((x0, y0)).T
    interp = np.vstack((x1, y1)).T

    # Make a distance matrix between pairwise observations
    # Note: from <http://stackoverflow.com/questions/1871536>
    # (Yay for ufuncs!)
    d0 = np.subtract.outer(obs[:,0], interp[:,0])
    d1 = np.subtract.outer(obs[:,1], interp[:,1])
    return np.hypot(d0, d1)

def pathSaved(location):
    new_string=location.split('\\')
    f_location=''
    for x in range(0,len(new_string)-1):
        f_location=f_location+str(new_string[x])+"\\"
    return f_location

##------------------------------------------------------------------------------------------------------------------------------------------------------------------
mxd=arcpy.mapping.MapDocument('CURRENT')
path=pathSaved(mxd.filePath)
start_date=arcpy.GetParameterAsText(0)
end_date=arcpy.GetParameterAsText(1)
freq=arcpy.GetParameterAsText(2)
boundary_input=arcpy.GetParameterAsText(3)
os.chdir(path)
CreateFolder('CMORPH')
outpath=os.path.join(path,'CMORPH')
os.chdir(outpath)
arcpy.env.workspace=outpath
st_date=datetime.strptime(start_date,'%m/%d/%Y')
en_date=datetime.strptime(end_date,'%m/%d/%Y')
arcpy.ProjectRaster_management(boundary_input,'wgs_boundary',arcpy.SpatialReference('WGS 1984'))
left_X=float(arcpy.GetRasterProperties_management('wgs_boundary','LEFT').getOutput(0))
right_X=float(arcpy.GetRasterProperties_management('wgs_boundary','RIGHT').getOutput(0))
bottom_y=float(arcpy.GetRasterProperties_management('wgs_boundary','BOTTOM').getOutput(0))
top_y=float(arcpy.GetRasterProperties_management('wgs_boundary','TOP').getOutput(0))
cell_size=float(arcpy.GetRasterProperties_management('wgs_boundary','CELLSIZEX').getOutput(0))
rows=int(arcpy.GetRasterProperties_management(boundary_input,'ROWCOUNT').getOutput(0))
cols=int(arcpy.GetRasterProperties_management(boundary_input,'COLUMNCOUNT').getOutput(0))
bbox=[left_X,bottom_y,right_X,top_y]


xll=[left_X+cell_size/2]
yll=[bottom_y+cell_size/2]
yl=bottom_y+cell_size/2
xl=left_X+cell_size/2

for i in range(rows-1):
    yl=yl+cell_size
    yll.append(yl)

for j in range(cols-1):
    xl=xl+cell_size
    xll.append(xl)

xll=np.array(xll)
yll=np.array(yll)

xi,yi=np.meshgrid(xll,yll)
xi,yi=xi.flatten(),yi.flatten()


urls='http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.CPC/.CMORPH/.daily/.mean/.morphed/.cmorph/dods'
res=0.25

arcpy.gp.addMessage('Trying to Connect....please wait!')

pds_1=netcdf.Dataset(urls)
pds=pydap.client.open_url(urls)
lat=pds['Y'][:]
lon=pds['X'][:]
lon[lon>180]-=360
tx=pds['T'][:]
t=pds_1.variables["T"]
tt=netcdf.num2date(tx,units=t.units)
i1,i2,j1,j2=spatialSubset(np.sort(lat)[::-1],np.sort(lon),res,bbox)
lati=np.argsort(lat)[::-1][i1:i2]
loni=np.argsort(lon)[j1:j2]
arcpy.gp.addMessage('Connected successfully.....!')
#arcpy.gp.addMessage(lati)
#arcpy.gp.addMessage(loni)

f=open('CMORPH_DAILY.BIN','wb+')

for dt in [st_date + timedelta(xx) for xx in range((en_date - st_date).days + 1)]:
    ti = [tj for tj in range(len(tt)) if tt[tj]>=dt]    
    

    if len(ti) > 0:
        arcpy.gp.addMessage(dt)
        data=pds['cmorph'][ti[0],lati[0]:lati[-1]+1,loni[0]:loni[-1]+1]
        dd=data['cmorph'][:]
        ddd=dd[0,:,:]
        ddd[ddd<0]=0
        
        lonx,latx=np.meshgrid(lon[loni],lat[lati])
        lonx,latx=lonx.flatten(),latx.flatten() 
        point=(np.array([lonx,latx])).T
        new_point=(np.array([xi,yi])).T

        interp_data=scipy.interpolate.NearestNDInterpolator(point,ddd.flatten())
        g_data=interp_data(new_point)
        gg_data=g_data.reshape((rows,cols))
        grid=np.flipud(gg_data)
        
        #np.savetxt('Data_'+str(ti[0])+'.txt',grid)
        grid_to_fortran=np.asfortranarray(grid,'float32')
        grid_to_fortran.tofile(f)
        
        #mynew_ras=arcpy.NumPyArrayToRaster(ddd.astype(float),arcpy.Point(lon[loni[0]]-0.25/2,lat[lati[-1]]-0.25/2),x_cell_size=0.25,y_cell_size=0.25)
        #mynew_ras.save('interpolate_'+str(ti[0])+'.tif')

        #mynew_ras=arcpy.NumPyArrayToRaster(grid.astype(float),arcpy.Point(left_X-cell_size/2,bottom_y-cell_size/2),x_cell_size=cell_size,y_cell_size=cell_size)
        #mynew_ras.save('interpolate10_'+str(ti[0])+'.tif')


f.close()
arcpy.Delete_management('wgs_boundary')