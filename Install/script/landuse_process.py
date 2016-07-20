import sys,os,csv,glob,zipfile,shutil,numpy,gzip

import arcpy
arcpy.CheckOutExtension("Spatial")
from arcpy.sa import *
from arcpy import env

def DeleteFile(workDir,fileName):
    os.chdir(workDir)
    for i in range(0,len(fileName)):
        if os.path.isdir(str(fileName[i]))==True:
            shutil.rmtree(str(fileName[i]))
        fileList=glob.glob(str(fileName[i])+".*")
        for f in fileList:
            os.remove(f)

def CreateFolder(folderName):
    if os.path.isdir(folderName)==True:
        shutil.rmtree(folderName)
        os.mkdir(folderName)
    else:
        os.mkdir(folderName)

def AddRasterLayer(path,rasterName,layerName):
    arcpy.MakeRasterLayer_management(Raster(os.path.join(path,rasterName)),layerName)
    mxd=arcpy.mapping.MapDocument("CURRENT")
    df=arcpy.mapping.ListDataFrames(mxd,'*')[0]
    addLayer=arcpy.mapping.Layer(layerName)
    arcpy.mapping.AddLayer(df,addLayer,'TOP')
    arcpy.Delete_management(addLayer)
    del mxd,df,addLayer


def pathSaved(location):
    new_string=location.split('\\')
    f_location=''
    for x in range(0,len(new_string)-1):
        f_location=f_location+str(new_string[x])+"\\"
    return f_location


def CreateHDR(folder_input,filename,nr,nc,ulx,uly,cellX,cellY):
    arcpy.gp.addMessage('Generating Header File...')
    f=open(os.path.join(folder_input,filename+'.hdr'),'w')
    f.write("BYTEORDER\tM\nLAYOUT\tBIL\nNROWS\t"+str(nr)+'\nNCOLS\t'+str(nc)+'\nNBANDS\t1\nNBITS\t8\nulxmap\t'+str(ulx)+'\nulymap\t'+str(uly)+'\nxdim\t'+str(cellX)+'\nydim\t'+str(cellY))
    f.close


def CreateProjection(folder_input,filename,lon_origin,lat_origin,radius):

    ff=open(os.path.join(folder_input,filename+'.prj'),'w')
    ff.write("PROJCS[\"GLCC_EuropeLAEA\",GEOGCS[\"GCS_Sphere_ARC_INFO\",DATUM[\"D_Sphere_ARC_INFO\",SPHEROID[\"Sphere_ARC_INFO\","+str(radius)+",0]],PRIMEM[\"Greenwich\",0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Lambert_Azimuthal_Equal_Area\"],PARAMETER[\"False_Easting\",0.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\","+str(lon_origin)+"],PARAMETER[\"Latitude_Of_Origin\","+str(lat_origin)+"],UNIT[\"Meter\",1.0]]")
    ff.close()

##------------------------------------------------------------------------------------------------------------------------------------------------------------------

region_input=arcpy.GetParameterAsText(0)
folder_input=arcpy.GetParameterAsText(1)
watershed=arcpy.GetParameterAsText(2)
os.chdir(folder_input)
list_tif=glob.glob('*2l20*.tif')
list_leg=glob.glob('*2l20*.leg')
img_file_name=list_tif[0].split('.')[0]
mxd=arcpy.mapping.MapDocument("CURRENT")
path=pathSaved(mxd.filePath)
os.chdir(path)
CreateFolder('Land_use')
current_path=os.path.join(path,'Land_use')
shutil.copy2(os.path.join(folder_input,list_leg[0]),os.path.join(current_path,'legend.leg'))
os.chdir(current_path)
env.workspace=current_path
env.overwriteOutput=True
ref=arcpy.Describe(Raster(watershed)).spatialReference
cell_size=arcpy.GetRasterProperties_management(watershed,"CELLSIZEX")
CreateFolder('temp_land')
env.workspace=os.path.join(current_path,'temp_land')


if region_input=='North America':
    CreateProjection(folder_input,img_file_name,100,50,6370997)


elif region_input=='South America':
    CreateProjection(folder_input,img_file_name,60,15,6370997)

elif region_input=='Europe':
    CreateProjection(folder_input,img_file_name,20,55,6370997)


elif region_input=='Asia':
    CreateProjection(folder_input,img_file_name,20,55,6370997)



elif region_input=='Australia Pacific':
    CreateProjection(folder_input,img_file_name,135,-15,6370997)



elif region_input=='Africa':
    CreateProjection(folder_input,img_file_name,20,5,6370997)



arcpy.ProjectRaster_management(os.path.join(folder_input,img_file_name+'.tif'),'projected',ref)
env.extent=watershed
arcpy.Resample_management('projected',"land_use",str(cell_size),'BILINEAR')
temp_land=ExtractByMask('land_use',watershed)
env.workspace=current_path
arcpy.RasterToASCII_conversion(temp_land,'land_use.asc')
temp_land.save('land_use')
AddRasterLayer(current_path,'land_use','Land use')
DeleteFile(current_path,['temp_land'])
arcpy.RefreshTOC()


