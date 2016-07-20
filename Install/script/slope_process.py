#Importing necessary Library including arcpy
import sys,os,csv,glob,math,shutil,arcpy
from arcpy.sa import *
from arcpy import env
import tempfile
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


def AddRasterLayer(path,rasterName,layerName):
    arcpy.MakeRasterLayer_management(Raster(os.path.join(path,rasterName)),layerName)
    mxd=arcpy.mapping.MapDocument("CURRENT")
    df=arcpy.mapping.ListDataFrames(mxd,'*')[0]
    addLayer=arcpy.mapping.Layer(layerName)
    arcpy.mapping.AddLayer(df,addLayer,'TOP')
    arcpy.Delete_management(addLayer)
    del mxd,df,addLayer


def clearINMEM():
    arcpy.env.workspace=r"IN_MEMORY"
    fcs=arcpy.ListFeatureClasses()
    tabs=arcpy.ListTables()
    ras=arcpy.ListRasters()

    for f in fcs:
        arcpy.Delete_management(f)

    for t in tabs:
        arcpy.Delete_management(t)

    for r in ras:
        arcpy.Delete_management(r)



def pathSaved(location):
    new_string=location.split('\\')
    f_location=''
    for x in range(0,len(new_string)-1):
        f_location=f_location+str(new_string[x])+"\\"
    return f_location


def main():
    INPUT_DEM=sys.argv[1]
    INPUT_fdr=sys.argv[2]
    INPUT_fac=sys.argv[3]
    INPUT_wshed=sys.argv[4]

    arcpy.env.overwriteOutput=True
    mxd=arcpy.mapping.MapDocument("CURRENT")
    WorkDir=pathSaved(mxd.filePath)
    os.chdir(WorkDir)
    CreateFolder('slope')
    tmp=open('info.txt','w')
    tmp.write(WorkDir)
    tmp.close()
    os.chdir(os.path.join(WorkDir,'slope'))
    #temp_dir=tempfile.mkdtemp()
    #temp_gdb='temp.gdb'
    #arcpy.CreateFileGDB_management(temp_dir,temp_gdb)
    #arcpy.env.workspace=os.path.join(temp_dir,temp_gdb)
    env.workspace=os.path.join(WorkDir,'slope')
    WorkDir=os.path.join(WorkDir,'slope')
    spatial_ref=arcpy.Describe(INPUT_DEM).spatialReference

    cell_size_coarse=arcpy.GetRasterProperties_management(INPUT_wshed,"CELLSIZEX")
    cell_size_fine=arcpy.GetRasterProperties_management(INPUT_DEM,"CELLSIZEX")
    Raster(INPUT_wshed).save('wshed')
    arcpy.env.extent=INPUT_wshed
    arcpy.env.mask=INPUT_wshed

    fill_dem=arcpy.sa.Fill(INPUT_DEM)
    fdir=arcpy.sa.FlowDirection(fill_dem)
    facc=arcpy.sa.FlowAccumulation(fdir,"#","INTEGER")

    arcpy.gp.addMessage('Processing for Coarse Resolution..')
    fdr_mask=ExtractByMask(INPUT_fdr,INPUT_wshed)
    fac_mask=ExtractByMask(INPUT_fac,INPUT_wshed)
    fdr_mask.save('fdr_coarse')
    fac_mask.save('fac_coarse')

    arcpy.env.addOutputsToMap=False
    arcpy.env.cellSize=float(cell_size_coarse.getOutput(0))
    #Slope Calculation

    thresold=1
    slope_raster=os.path.join(WorkDir,"slope_coarse")
    ttt=os.path.join(WorkDir,"ttt_raster")
    arcpy.env.nodata='NONE'
    times=int(cell_size_coarse.getOutput(0))/int(cell_size_fine.getOutput(0))
    arcpy.gp.addMessage('Slope Calculation....')
    angle=arcpy.sa.Slope(fill_dem,"DEGREE")
    degree=BlockStatistics(angle,NbrRectangle(times,times),"MEAN")
    angle.save(os.path.join(WorkDir,'slope_fine'))
    arcpy.Resample_management(degree,slope_raster,cell_size_coarse,"NEAREST")
    stream=Con(facc>thresold,fdir)
    arcpy.Delete_management(angle,'')
    del angle
    arcpy.Delete_management(degree,'')
    del degree
    #arcpy.gp.addMessage('Calculating Distance..')

    t=[]
    for i in range(0,4):
        a=4**i
        res="t"+str(a)
        print "Creating..."+res
        t.append(Con(stream==a,int(cell_size_fine.getOutput(0))))

    for j in range(1,8,2):
        b=2**j
        res="t"+str(b)
        print "Creating..."+res
        t.append(Con(stream==b,int(cell_size_fine.getOutput(0))*1.414))


    tt=CellStatistics(t,"MEAN","DATA")
    sum1=BlockStatistics(tt,NbrRectangle(times,times),"SUM")
    arcpy.Resample_management(sum1,ttt,cell_size_coarse,"NEAREST")
    outRaster=CreateConstantRaster(int(cell_size_coarse.getOutput(0)),'FLOAT',int(cell_size_coarse.getOutput(0)),fill_dem)
    cell_Area=(outRaster*outRaster)/(1000**2)
    arcpy.DefineProjection_management(cell_Area,spatial_ref)
    cell_Area.save(os.path.join(WorkDir,'cell_area'))
    slope_length=(cell_Area*1000**2)/(Raster(ttt)*2)
    slope_length.save(os.path.join(WorkDir,'slope_length'))
    arcpy.RasterToASCII_conversion(Raster(slope_raster),os.path.join(WorkDir,'slope_angle.asc'))
    arcpy.RasterToASCII_conversion(slope_length,os.path.join(WorkDir,'slope_length.asc'))
    bedslope=BlockStatistics(Raster(slope_raster),NbrRectangle(times,times),"MEAN")
    arcpy.RasterToASCII_conversion(bedslope,os.path.join(WorkDir,'bedslope.asc'))
    bedslope.save(os.path.join(WorkDir,'bedslope'))
    arcpy.Delete_management('ttt_raster')
    arcpy.Delete_management(tt)

    for i in t:
        arcpy.Delete_management(i,'')
    del t
    arcpy.gp.addMessage('Finished Slope Calculation..')

    mxd=arcpy.mapping.MapDocument("CURRENT")
    df=arcpy.mapping.ListDataFrames(mxd,'*')[0]
    lyr=arcpy.mapping.ListLayers(mxd,'*',df)

    for i in lyr:
        if i.name=='Flow_Accum':
            arcpy.mapping.RemoveLayer(df,i)

        if i.name=='Flow_dir':
            arcpy.mapping.RemoveLayer(df,i)

        if i.name=='Fill_DEM':
            arcpy.mapping.RemoveLayer(df,i)

    arcpy.RefreshTOC()
    AddRasterLayer(WorkDir,'fac_coarse','accum')
    AddRasterLayer(WorkDir,'fdr_coarse','fdir')
    AddRasterLayer(WorkDir,'bedslope','Coarse Bedslope')
    arcpy.RefreshTOC()

    arcpy.Delete_management('in_memory')
    clearINMEM()
    arcpy.RefreshTOC()
    arcpy.RefreshActiveView()

    for im in lyr:
        if i.name=='GP*':
            arcpy.mapping.RemoveLayer(df,im)
            arcpy.gp.addMessage('True')



if __name__ == "__main__":
    try:
        main()
    except Exception, e:
        import gc
        gc.collect()
        import traceback
        arcpy.AddError(traceback.format_exc())



