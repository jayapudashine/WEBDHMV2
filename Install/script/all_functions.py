import sys,os,csv,glob,math,shutil,arcpy
from arcpy.sa import *
from arcpy import env

def DeleteFile(path,fileName):
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


def AddRasterLayer(path,layerName):
    layer=os.path.join(path,'new'+str(layerName)+'.lyr')
    mxd=arcpy.mapping.MapDocument("CURRENT")
    df=arcpy.mapping.ListDataFrames(mxd,'*')[0]
    arcpy.MakeRasterLayer_management(Raster(layerName),layer)
    newlayer=arcpy.mapping.Layer(layer)
    arcpy.mapping.AddLayer(df,newlayer,'TOP')
    new_name=arcpy.mapping.ListLayers(mxd,newlayer,df)
    new_name[0].name=str(layerName)



def pathSaved(location):
    new_string=location.split('\\')
    f_location=''
    for x in range(0,len(new_string)-1):
        f_location=f_location+str(new_string[x])+"\\"
    return f_location


