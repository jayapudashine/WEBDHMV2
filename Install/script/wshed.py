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
    outlet=sys.argv[1]
    fdr=sys.argv[2]
    fac=sys.argv[3]

    arcpy.env.overwriteOutput=True
    arcpy.gp.overwriteOutput=True
    mxd=arcpy.mapping.MapDocument("CURRENT")
    WorkDir=all_functions.pathSaved(mxd.filePath)
    os.chdir(WorkDir)
    work_dir=os.path.join(WorkDir,'watershed')
    arcpy.env.workspace=work_dir
    arcpy.env.extent=fdr
    wshed_poly=os.path.join(work_dir,'wtrshed_poly.shp')
    cell_size_coarse=arcpy.GetRasterProperties_management(fac,"CELLSIZEX").getOutput(0)
    snapPour=SnapPourPoint(outlet,fac,0,'#')
    watershed=Watershed(fdr,snapPour,'VALUE')
    wtrshed=Con(watershed==0,1)
    arcpy.RasterToPolygon_conversion(wtrshed,wshed_poly,'NO_SIMPLIFY','VALUE')
    #wtrshd=ExtractByMask(wtrshed,wshed_poly)
    arcpy.Clip_management(wtrshed,'#','wsheds',wshed_poly,'0','ClippingGeometry')
    arcpy.ProjectRaster_management('wsheds','wsheds_wgs',arcpy.SpatialReference('WGS 1984'))
    AddRasterLayer(work_dir,'wsheds','wshed')


if __name__ == "__main__":
    try:
        main()
    except Exception, e:
        import gc
        gc.collect()
        import traceback
        arcpy.AddError(traceback.format_exc())


