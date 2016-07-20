import all_functions,os
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
    del mxd,df,addLayer


def AddFeatureLayer(WorkDir,layerName):
    mxd=arcpy.mapping.MapDocument("CURRENT")
    df=arcpy.mapping.ListDataFrames(mxd,'*')[0]
    newlayer=arcpy.mapping.Layer(os.path.join(WorkDir,layerName+'.shp'))
    arcpy.mapping.AddLayer(df,newlayer,'TOP')
    arcpy.RefreshActiveView()
    arcpy.RefreshTOC()
    del mxd,df,newlayer


def main():
    dem=sys.argv[1]
    cell_size=sys.argv[2]
    thresold=sys.argv[3]
    arcpy.env.overwriteOutput=True
    arcpy.gp.overwriteOutput=True
    spatial_ref=arcpy.Describe(dem).spatialReference
    mxd=arcpy.mapping.MapDocument("CURRENT")
    WorkDir=all_functions.pathSaved(mxd.filePath)
    os.chdir(WorkDir)
    work_dir=os.path.join(WorkDir,'watershed')
    arcpy.env.workspace=work_dir

    fill=arcpy.sa.Fill(dem)
    arcpy.Resample_management(fill,'dem_'+str(cell_size),cell_size)
    #arcpy.env.extent=wshed_poly
    arcpy.gp.addMessage('Fill DEM....')
    fill_dem=arcpy.sa.Fill(Raster('dem_'+str(cell_size)))
    arcpy.gp.addMessage('Flow Direction....')
    fdir=arcpy.sa.FlowDirection(fill_dem)
    fdir.save('fdr_dem')
    AddRasterLayer(work_dir,'fdr_dem','Flow_dir')
    arcpy.gp.addMessage('Flow Accumulation...')
    facc=arcpy.sa.FlowAccumulation(fdir)
    facc.save('fac_dem')
    AddRasterLayer(work_dir,'fac_dem','Flow_Accum')
    max_accum=arcpy.GetRasterProperties_management(facc,"MAXIMUM")
    #thresold=float(max_accum.getOutput(0))*0.01
    arcpy.gp.addMessage(thresold)
    strm=Con(facc>int(thresold),1)
    arcpy.sa.StreamToFeature(strm,fdir,'stream','NO_SIMPLIFY')
    AddFeatureLayer(work_dir,'stream')


if __name__ == "__main__":
    try:
        main()
    except Exception, e:
        import gc
        gc.collect()
        import traceback
        arcpy.AddError(traceback.format_exc())









