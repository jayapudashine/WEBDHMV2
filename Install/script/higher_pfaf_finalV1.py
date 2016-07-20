import sys,os,csv,glob,zipfile,shutil,numpy

sys.path.append(r"C:\Program Files (x86)\ArcGIS\Desktop10.1\bin")
sys.path.append(r"C:\Program Files (x86)\ArcGIS\Desktop10.1\ArcToolbox\Scripts")
sys.path.append(r"C:\Program Files (x86)\ArcGIS\Desktop10.1\bin")
sys.path.append(r"C:\Program Files (x86)\ArcGIS\Desktop10.1\arcpy")
sys.path.append(r"C:\Program Files (x86)\ArcGIS\Desktop10.1\lib")

import arcpy
arcpy.CheckOutExtension("Spatial")
from arcpy.sa import *
from arcpy import env


##---------------------------------------------------------------
def CreateFolder(folderName):
    if os.path.isdir(folderName)==True:
        shutil.rmtree(folderName)
        os.mkdir(folderName)
    else:
        os.mkdir(folderName)


def pathFortran(location):
    new_string=location.split('\\')
    f_location=''
    for x in range(0,len(new_string)):
        f_location=f_location+str(new_string[x])+"/"
    return f_location


def floatToSci(num):
    x=format(num,'0.14E')
    A=str(x)
    exp=A.find('E+')
    converted='0.'+A[0]+A[2:exp]+'E+'+str(int(A[exp+2:])+1)
    return converted



def DeleteFile(workDir,fileName):
    os.chdir(workDir)
    for i in range(0,len(fileName)):
        if os.path.isdir(str(fileName[i]))==True:
            shutil.rmtree(str(fileName[i]))
        fileList=glob.glob(str(fileName[i])+".*")
        for f in fileList:
            os.remove(f)


def MaskRaster(location,basin,OrgRaster):
    os.chdir(location)
    mask_ras=ExtractByMask(Raster(basin),Raster(OrgRaster))
    mask_ras.save(str(OrgRaster))


def RasterToText(workDir,raster,TextFileName,shapefile,acc,link_raster):

    arcpy.env.overwriteOutput=True
    os.chdir(workDir)
    CreateFolder('temp_log')
    new_Rpath=os.path.join(workDir,'temp_log')
    temp_workDir=os.path.join(workDir,'temp')
    fc=os.path.join(new_Rpath,'new'+str(raster)+'.shp')
    shp=os.path.join(new_Rpath,'shape'+str(raster)+'.shp')
    #shape_new=os.path.join(new_Rpath,'newshape'+str(raster)+'.shp')
    arcpy.RasterToPoint_conversion(raster,fc,'VALUE')
    ExtractMultiValuesToPoints(fc,[Raster(acc),link_raster])
    arcpy.FeatureVerticesToPoints_management(shapefile,shp,'END')
    ExtractMultiValuesToPoints(shp,[Raster(acc),link_raster])

    os.chdir(workDir)
    #For End Point of the segment
    f=['GRID_CODE','SHAPE@X','SHAPE@Y','ACC','LINK']
    st_pnt=[]
    with arcpy.da.SearchCursor(shp,f) as cu:
        for r in cu:
            st_pnt.append([r[0],r[1],r[2],r[3],r[4]])

    # For other points
    fields=['GRID_CODE','SHAPE@X','SHAPE@Y','ACC','LINK']
    x=[]
    with arcpy.da.SearchCursor(fc,fields) as cursor:
        for row in cursor:
            x.append([row[0],row[1],row[2],row[3],row[4]])


    field=['GRID_CODE']
    grid_code=[]
    with arcpy.da.SearchCursor(shapefile,field) as cursor:
        for row in cursor:
            grid_code.append(row[0])

    new_arry=numpy.array(x)
    new_pnt=numpy.array(st_pnt)
    textfile=os.path.join(workDir,TextFileName)
    outFile=open(textfile,'w')

    unique=[]
    new=[]
    for x,i in enumerate(grid_code):
        mask_list=new_arry[numpy.where(new_arry[:,0]==i)[0],:]
        k=numpy.lexsort((mask_list[:,3],mask_list[:,0]))
        m_list=mask_list[k]
        unique_mask=numpy.unique(m_list[:,4]).tolist()
        unique_mask.extend([i])

        if len(unique_mask)>2:
            unique.append([i])
            new_unique=numpy.array(unique)
            nq=new_unique[numpy.where(new_unique[:,0]==i)[0]]

            if len(nq)>=1:
                b=len(nq)
                a=b-1
                for j in range(a,b):
                    p_list=numpy.where(m_list[:,4]==unique_mask[j])[0]
                    n_list=m_list[p_list,:]
                    k_list=numpy.where(new_pnt[:,0]==i)[0]
                    mask_p_list=new_pnt[k_list,:]
                    if x>=len(grid_code)-1:
                        f_list=mask_p_list
                    else:
                        f_list=numpy.concatenate((n_list,mask_p_list),axis=0)
                    outFile.writelines('\t'+str(int(i))+'\n')
                    for p in f_list:
                        outFile.writelines('\t'+str(p[1])+'\t'+str(p[2])+'\n')
                    outFile.writelines('END'+'\n')
        else:
            k_list=numpy.where(new_pnt[:,0]==i)[0]
            mask_p_list=new_pnt[k_list,:]
            n_list=numpy.concatenate((m_list,mask_p_list),axis=0)
            outFile.writelines('\t'+str(int(i))+'\n')

            for p in n_list:
                outFile.writelines('\t'+str(p[1])+'\t'+str(p[2])+'\n')

            outFile.writelines('END'+'\n')

    outFile.writelines('END')
    outFile.close()


def PreProcessPfaf(workDir,level,subBasin,thresold,flowACU,flowDir):

    slope_path=os.path.join(workDir,'slope')
    pfaf_path=os.path.join(workDir,'pfafstetter')
    os.chdir(pfaf_path)
    pfaf_basin=str(subBasin[1:])
    #flowDir=os.path.join(slope_path,'dir')
    #flowACU=os.path.join(slope_path,'acc')
    arcpy.env.mask=subBasin

    if level==2:
		arcpy.gp.addMessage("your level"+str(level))
        CreateFolder('basin'+pfaf_basin)
        temp_basin=os.path.join(pfaf_path,'basin'+pfaf_basin)
        os.chdir(temp_basin)
        CreateFolder('temp')
        temp_workDir=os.path.join(temp_basin,'temp')
        env.workspace=temp_workDir

    if level==3:
        t_basin=os.path.join(pfaf_path,'basin'+str(pfaf_basin[0]))
        os.chdir(t_basin)
        CreateFolder('basin'+pfaf_basin)
        temp_basin=os.path.join(t_basin,'basin'+str(pfaf_basin))
        os.chdir(temp_basin)
        CreateFolder('temp')
        temp_workDir=os.path.join(temp_basin,'temp')
        env.workspace=temp_workDir

    if level==4:
        t_basin=os.path.join(pfaf_path,'basin'+str(pfaf_basin[0]),'basin'+str(pfaf_basin[0:2]))
        os.chdir(t_basin)
        CreateFolder('basin'+pfaf_basin)
        temp_basin=os.path.join(t_basin,'basin'+str(pfaf_basin))
        os.chdir(temp_basin)
        CreateFolder('temp')
        temp_workDir=os.path.join(temp_basin,'temp')
        env.workspace=temp_workDir

    arcpy.gp.addMessage('Start Processing...')
    flow_Len=FlowLength(Raster(flowDir),'DOWNSTREAM')
    net_thresold=Con(Raster(flowACU)>thresold,1)
    link=StreamLink(net_thresold,Raster(flowDir))
    link.save('link')

    #arcpy.gp.addMessage('Zonal Statistics....')
    net_acc=Int(ZonalStatistics(link,'VALUE',Raster(flowACU),'MAXIMUM'))
    net_acc.save('net_acc')
    net_dis=Int(ZonalStatistics(link,'VALUE',flow_Len,'MINIMUM'))
    net_dis.save('net_dis')

    #arcpy.gp.addMessage('Stream to Feature......')
    lk=StreamToFeature(link,Raster(flowDir),'lk','NO_SIMPLIFY')
    lacc=StreamToFeature(net_acc,Raster(flowDir),'lacc','NO_SIMPLIFY')
    ldis=StreamToFeature(net_dis,Raster(flowDir),'ldis','NO_SIMPLIFY')


    #arcpy.gp.addMessage('Generating Text File...')
    RasterToText(temp_basin,Raster('link'),'l'+str(thresold)+'.txt','lk.shp',flowACU,Raster('link'))
    RasterToText(temp_basin,Raster('net_acc'),'a'+str(thresold)+'.txt','lacc.shp',flowACU,Raster('link'))
    RasterToText(temp_basin,Raster('net_dis'),'d'+str(thresold)+'.txt','ldis.shp',flowACU,Raster('link'))
    DeleteFile(temp_basin,['temp_log'])


def CreateSubBasin(workDir,BasinNo,flowDir,flowACU):

    spatial_ref=arcpy.Describe(Raster(flowDir)).spatialReference
    flowA=ExtractByMask(Raster(flowACU),Raster(BasinNo))
    flowD=ExtractByMask(Raster(flowDir),Raster(BasinNo))
    basin=str(BasinNo[1:])

    os.chdir(workDir)
    arcpy.env.workspace=workDir

    op_file=open('outlet.txt','r')
    lines=op_file.readlines()
    z=[]
    for i in range(0,len(lines)-1):
        z.append(lines[i].strip().split())

    if len(z)==9:
        try:
            with open('output.txt','wb') as f:
                writer=csv.DictWriter(f,fieldnames=['Level','Lon','Lat','Basin_No'])
                writer.writeheader()
                writer=csv.writer(f)
                writer.writerows(z)

            pointFC='sub_basin.shp'
            arcpy.gp.addMessage('Creating Sub Basins...')
            arcpy.CreateFeatureclass_management(workDir,pointFC,"POINT","","","",spatial_ref)
            arcpy.AddField_management(pointFC,"Basin_NO","INTEGER","","")

            pointAdd=open('output.txt','r')
            headerLine=pointAdd.readline()
            valueList=headerLine.strip().split(",")
            print valueList

            latValueIndex=valueList.index('Lat')
            lonValueIndex=valueList.index('Lon')
            basinValueIndex=valueList.index('Basin_No')
            cursor=arcpy.InsertCursor(pointFC)

            for point in pointAdd.readlines():
                segmentedPoint=point.split(",")
                latValue=segmentedPoint[latValueIndex]
                lonValue=segmentedPoint[lonValueIndex]
                basinValue=segmentedPoint[basinValueIndex]
                vertex=arcpy.CreateObject("Point")
                vertex.X=lonValue
                vertex.Y=latValue
                feature=cursor.newRow()
                feature.shape=vertex
                feature.Basin_No=int(str(basin+basinValue))
                cursor.insertRow(feature)
            del cursor
        except:
            arcpy.gp.addMessage('Pfafstatetter Sub Basin Division is not possible...')

    #arcpy.gp.addMessage('Snapping Point for Sub Basin Division...')
    temp_pnt=SnapPourPoint(pointFC,flowACU,200,'Basin_NO')
    ws_all=Watershed(flowD,temp_pnt,"Value")
    ws_all.save('W_all'+str(basin))
    arcpy.RasterToPolygon_conversion(ws_all,'wsall_poly'+str(basin),'NO_SIMPLIFY',"Value")

    #arcpy.gp.addMessage('Sub Basin Division....')
    w=[]
    field=['BASIN_NO']
    b_code=[]
    with arcpy.da.SearchCursor(pointFC,field) as cursor:
        for row in cursor:
            b_code.append(row[0])

    for j,i in enumerate(b_code):
        w.append((Con(ws_all==i,i)))
        w[j].save('w'+str(i))


    b_code.sort()
    for i in b_code:
        AddRasterLayer(workDir,'w'+str(i))

    AddRasterLayer(workDir,'W_all'+str(basin))
    arcpy.RefreshTOC()


def AddFeatureLayer(WorkDir,layerName):
    os.chdir(WorkDir)
    layer=os.path.join(WorkDir,str(layerName))
    mxd=arcpy.mapping.MapDocument("CURRENT")
    df=arcpy.mapping.ListDataFrames(mxd,'*')[0]
    arcpy.MakeFeatureLayer_management(layerName,layer)
    newlayer=arcpy.mapping.Layer(layer)
    arcpy.mapping.AddLayer(df,newlayer,"TOP")
    newlayer.showLabels=True
    arcpy.gp.addMessage(newlayer.symbologyType)
    arcpy.RefreshTOC()


def AddRasterLayer(path,layerName):
    arcpy.env.workspace=path
    layer='S'+str(layerName[1:])
    mxd=arcpy.mapping.MapDocument("CURRENT")
    df=arcpy.mapping.ListDataFrames(mxd,'*')[0]
    arcpy.MakeRasterLayer_management(Raster(layerName),layer)
    newlayer=arcpy.mapping.Layer(layer)
    arcpy.mapping.AddLayer(df,newlayer,'TOP')
    arcpy.Delete_management(newlayer)
    del layer,mxd,df


def pathSaved(location):
    new_string=location.split('\\')
    f_location=''
    for x in range(0,len(new_string)-1):
        f_location=f_location+str(new_string[x])+"\\"
    return f_location

##----------------------------------------------------------------------------


try:
    #input parameters
    mxd=arcpy.mapping.MapDocument("CURRENT")
    path=pathSaved(mxd.filePath)
    os.chdir(path)
    pfaf_level=int(arcpy.GetParameterAsText(0))
    BasinNo=arcpy.GetParameterAsText(1).split(';')
    thresold=int(arcpy.GetParameterAsText(2))
    slopepath=os.path.join(path,'slope')
    pfaf_path=os.path.join(path,'pfafstetter')
    flowD=os.path.join(pfaf_path,'dir')
    flowA=os.path.join(pfaf_path,'acc')
    cell_size=arcpy.GetRasterProperties_management(Raster(flowA),"CELLSIZEX")

    for bsn in BasinNo:
        bsn_no=str(bsn[1:])
        arcpy.gp.addMessage('Process for Basin'+bsn_no)
        PreProcessPfaf(path,pfaf_level,bsn,thresold,flowA,flowD)

        import pfafst as pf
        arcpy.gp.addMessage('imported')
	pfaf_path=os.path.join(path,'pfafstetter')
        os.chdir(pfaf_path)
		
        if pfaf_level==2:
            pf.maincalculation(2,int(bsn_no),-9,-9,-9,-9,-9,-9,cell_size,str(thresold))
            npath=os.path.join(pfaf_path,'basin'+str(bsn_no))

        if pfaf_level==3:
            pf.maincalculation(3,int(bsn_no[0]),int(bsn_no[1]),-9,-9,-9,-9,-9,cell_size,str(thresold))
            npath=os.path.join(pfaf_path,'basin'+str(bsn_no[0]),'basin'+str(bsn_no))

        if pfaf_level==4:
            pf.maincalculation(4,int(bsn_no[0]),int(bsn_no[1]),int(bsn_no[2]),-9,-9,-9,-9,cell_size,str(thresold))
            npath=os.path.join(pfaf_path,'basin'+str(bsn_no[0]),'basin'+str(bsn_no[0:2]),'basin'+str(bsn_no))
            arcpy.gp.addMessage(npath)

        CreateSubBasin(npath,bsn,flowD,flowA)


except:
    arcpy.gp.addMessage('Error Processing')
