#Importing necessary Library including arcpy
import sys,os,csv,glob,math,shutil,arcpy
from arcpy.sa import *
from arcpy import env

#Check for Spatial Analyst Extension
arcpy.CheckOutExtension("Spatial")


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


#workpath and temporary folder defination

INPUT_fineDEM=sys.argv[1]
INPUT_wshed=sys.argv[2]
cell_size=sys.argv[3]

try:
    # Main program starts
    fine=INPUT_fineDEM
    wshed=INPUT_wshed
    arcpy.env.overwriteOutput=True
    mxd=arcpy.mapping.MapDocument("CURRENT")
    WorkDir=pathSaved(mxd.filePath)
    os.chdir(WorkDir)
    if WorkDir!='':
        CreateFolder('slope')
        tmp=open('info.txt','w')
        tmp.write(WorkDir)
        tmp.close()
        os.chdir(os.path.join(WorkDir,'slope'))
        env.workspace=os.path.join(WorkDir,'slope')
        WorkDir=os.path.join(WorkDir,'slope')
        spatial_ref=arcpy.Describe(fine).spatialReference
        cell_size_coarse=arcpy.GetRasterProperties_management(Raster(wshed),"CELLSIZEX")
        Raster(fine).save('fine')
        Raster(wshed).save('wshed')
        arcpy.env.mask=wshed
        arcpy.Resample_management(fine,'coarse_dem',cell_size,'CUBIC')
        arcpy.gp.addMessage('Filling...')
        fill_dem=arcpy.sa.Fill(fine)
        fill_dem.save('fill')
        fill_dem_coarse=arcpy.sa.Fill(Raster('coarse_dem'))
        fill_dem_coarse.save('fill_coarse')
        arcpy.gp.addMessage('Finished Filling DEM')
        arcpy.gp.addMessage('Flow Direction....')
        fdr=arcpy.sa.FlowDirection(fill_dem)
        fdr.save('fdr')
        arcpy.gp.addMessage('Flow Accumulation...')
        fac=arcpy.sa.FlowAccumulation(fdr,"#","INTEGER")
        fac.save('fac')
        arcpy.gp.addMessage('Processing for Coarse Resolution...')
        arcpy.env.cellSize=float(cell_size_coarse.getOutput(0))
        arcpy.gp.addMessage('Fill DEM for Coarse Resolution')
        fill_coarse=arcpy.sa.Fill(fine)
        fill_coarse.save('fill')
        flowDir=arcpy.sa.FlowDirection(fill_coarse)
        flowDir.save('dir')
        flowACU=arcpy.sa.FlowAccumulation(flowDir,"#","INTEGER")
        flowACU.save('acc')
        arcpy.gp.addMessage('Finished all')
        AddRasterLayer(WorkDir,'acc')
        AddRasterLayer(WorkDir,'dir')
        arcpy.RefreshTOC()


except Exception, ErrorDesc:
    arcpy.gp.addMessage('Error in processing... Please follow the steps carefully')
    arcpy.gp.addMessage('File is not Saved..Please save the Map file in the location where you want to create all input files for WEB-DHM')
