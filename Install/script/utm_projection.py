#-------------------------------------------------------------------------------
# Name:        WEBDHM Toolbox
# Purpose:     Preprocessing for WEB DHM Model
# Author:      Jayaram Pudashine
# Created:     15/05/2015
# Copyright:   (c) 2016
# Updated:     03/06/2016
#-------------------------------------------------------------------------------

import os,all_functions,glob
from arcpy.sa import *
#Check for Spatial Analyst Extension
arcpy.CheckOutExtension("Spatial")
from arcpy import *


def AddRasterLayer(path,rasterName,layerName):
    arcpy.MakeRasterLayer_management(Raster(os.path.join(path,rasterName)),layerName)
    mxd=arcpy.mapping.MapDocument("CURRENT")
    df=arcpy.mapping.ListDataFrames(mxd,'*')[0]
    addLayer=arcpy.mapping.Layer(layerName)
    arcpy.mapping.AddLayer(df,addLayer,'TOP')
    arcpy.Delete_management(addLayer)
    #arcpy.mapping.RemoveLayer(df,addLayer)
    del mxd,df


def AddFeatureLayer(WorkDir,layerName):
    mxd=arcpy.mapping.MapDocument("CURRENT")
    df=arcpy.mapping.ListDataFrames(mxd,'*')[0]
    newlayer=arcpy.mapping.Layer(os.path.join(WorkDir,layerName+'.shp'))
    arcpy.mapping.AddLayer(df,newlayer,'TOP')
    arcpy.RefreshActiveView()
    arcpy.RefreshTOC()
    del mxd,df,newlayer


def main():
    raw_dem=sys.argv[1]
    spatial_ref=sys.argv[2]
    cellsize=sys.argv[3]
    arcpy.env.overwriteOutput=True
    arcpy.gp.overwriteOutput=True
    #arcpy.gp.addMessage(arcpy.env.workspace)
    os.chdir(arcpy.env.workspace)
    list_temp=glob.glob('*.*')

    for f in list_temp:
        os.unlink(f)

    mxd=arcpy.mapping.MapDocument("CURRENT")
    WorkDir=all_functions.pathSaved(mxd.filePath)
    os.chdir(WorkDir)
    all_functions.CreateFolder('watershed')
    work_dir=os.path.join(WorkDir,'watershed')
    arcpy.env.workspace=work_dir
    ProjectRaster_management(raw_dem,'projected_dem',spatial_ref,cell_size=cellsize)
    AddRasterLayer(work_dir,'projected_dem','DEM_Projected')


if __name__ == "__main__":
    try:
        main()
    except Exception, e:
        import gc
        gc.collect()
        import traceback
        arcpy.AddError(traceback.format_exc())



