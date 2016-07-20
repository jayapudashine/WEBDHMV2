#Importing necessary Library including arcpy

import sys,os,csv,glob,math,shutil,arcpy,all_functions
from arcpy.sa import *
from arcpy import env
import catchment
import numpy as np
#Check for Spatial Analyst Extension
arcpy.CheckOutExtension("Spatial")
import morph,param

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


def AddRasterLayer(path,rasterName,layerName):
    arcpy.MakeRasterLayer_management(Raster(os.path.join(path,rasterName)),layerName)
    mxd=arcpy.mapping.MapDocument("CURRENT")
    df=arcpy.mapping.ListDataFrames(mxd,'*')[0]
    addLayer=arcpy.mapping.Layer(layerName)
    arcpy.mapping.AddLayer(df,addLayer,'TOP')
    arcpy.Delete_management(addLayer)
    del mxd,df,addLayer


Input_bedslope=sys.argv[1]
Input_kfs=sys.argv[2]
Input_subcatchment=sys.argv[3]
dx=int(sys.argv[4])

rows=int(arcpy.GetRasterProperties_management(Input_bedslope,'ROWCOUNT').getOutput(0))
cols=int(arcpy.GetRasterProperties_management(Input_bedslope,'COLUMNCOUNT').getOutput(0))

mxd=arcpy.mapping.MapDocument("CURRENT")
WorkDir=all_functions.pathSaved(mxd.filePath)
os.chdir(WorkDir)
work_dir=os.path.join(WorkDir,'pfafstetter')
os.chdir(work_dir)
arcpy.env.workspace=work_dir


shutil.copy(Input_kfs,work_dir)

try:
    import catchment
    catchment.sub_catchment()

except:
    arcpy.gp.addMessage('Error')


workspace=work_dir
os.chdir(workspace)
count=0
l=[]
with open('subcatchment.dat','r') as f:
    for line in f:
       l.append(line)

CreateFolder('model')
arcpy.env.workspace=workspace
for i in range(0,len(l)):
    lev1=int(l[i].split()[1][2])
    lev2=int(l[i].split()[1][3])
    lev3=int(l[i].split()[1][4])
    new_dir='sub_ws'+str(lev1)+str(lev2)+str(lev3)
    CreateFolder(new_dir)



arcpy.gp.addMessage('Processing for...')
fdir=Raster(os.path.join(workspace,'dir'))
dis=FlowLength(fdir,'DOWNSTREAM')


for i in range(0,len(l)):
    lev1=int(l[i].split()[1][2])
    lev2=int(l[i].split()[1][3])
    lev3=int(l[i].split()[1][4])

    arcpy.env.overwrite=True
    new_dir='sub_ws'+str(lev1)+str(lev2)+str(lev3)
    sub=Raster(os.path.join(workspace,'w'+str(lev1)))
    new_workspace=os.path.join(workspace,new_dir)

    if lev2<1 and lev3<1:
        arcpy.env.workspace=new_workspace
        dis_mask=ExtractByMask(dis,sub)
        bedslope_mask=ExtractByMask(Input_bedslope,sub)
        arcpy.RasterToASCII_conversion(sub,'watershed.asc')
        arcpy.RasterToASCII_conversion(dis_mask,'distance.asc')
        arcpy.RasterToASCII_conversion(bedslope_mask,'bedslope.asc')

    elif lev2>=1 and lev3<1:
        temp_workspace=os.path.join(workspace,'basin'+str(lev1))
        sub=Raster(os.path.join(temp_workspace,'w'+str(lev1)+str(lev2)))
        arcpy.env.workspace=new_workspace
        dis_mask=ExtractByMask(dis,sub)
        bedslope_mask=ExtractByMask(Input_bedslope,sub)
        arcpy.RasterToASCII_conversion(sub,'watershed.asc')
        arcpy.RasterToASCII_conversion(dis_mask,'distance.asc')
        arcpy.RasterToASCII_conversion(bedslope_mask,'bedslope.asc')

    elif lev2>=1 and lev3>=1:
        temp_workspace=os.path.join(workspace,'basin'+str(lev1),'basin'+str(lev1)+str(lev2))
        sub=Raster(os.path.join(temp_workspace,'w'+str(lev1)+str(lev2)+str(lev3)))
        arcpy.env.workspace=new_workspace
        dis_mask=ExtractByMask(dis,sub)
        bedslope_mask=ExtractByMask(Input_bedslope,sub)
        arcpy.RasterToASCII_conversion(sub,'watershed.asc')
        arcpy.RasterToASCII_conversion(dis_mask,'distance.asc')
        arcpy.RasterToASCII_conversion(bedslope_mask,'bedslope.asc')

    arcpy.gp.addMessage('sub_ws'+str(lev1)+str(lev2)+str(lev3))

arcpy.gp.addMessage('Generating necessary binary files...')
os.chdir(work_dir)
arcpy.env.workspace=work_dir
morph.morph(cols,rows)
shutil.copy(Input_subcatchment,os.path.join(work_dir,'model'))
os.chdir(os.path.join(work_dir,'model'))
arcpy.env.workspace=os.path.join(work_dir,'model')
param.parameter_cal(cols,rows,dx)















