import sys,os,csv,glob,math,shutil,arcpy,numpy,subprocess,time,lai
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


def pathSaved(location):
    new_string=location.split('\\')
    f_location=''
    for x in range(0,len(new_string)-1):
        f_location=f_location+str(new_string[x])+"\\"
    return f_location



def parameter_file(location,filename,x0,x1,y0,y1,projection,zone):

    outputname=filename.split(".")[1][1:]
    param=open('param.prm','w')
    arcpy.gp.addMessage(outputname)
    param.writelines("\n"
    +
    "INPUT_FILENAME = " + os.path.join(location,filename)
    + "\n\n"+
    "SPECTRAL_SUBSET = ( 1 1 0 0 0 0 )"
    + "\n\n"+
    "SPATIAL_SUBSET_TYPE = OUTPUT_PROJ_COORDS"
    + "\n\n"+
    "SPATIAL_SUBSET_UL_CORNER = ( "+str(x0)+" "+str(y0)+" )\n"
    +"SPATIAL_SUBSET_LR_CORNER = ( "+str(x1)+" "+str(y1)+" )\n"
    +"\n"+

    "OUTPUT_FILENAME ="+os.path.join(location,outputname+'.tif')
    +"\n\n"+
    "RESAMPLING_TYPE = NEAREST_NEIGHBOR"
    +"\n\n"+
    "OUTPUT_PROJECTION_TYPE = "+projection
    +"\n\n"+
    "OUTPUT_PROJECTION_PARAMETERS = (\n"
     +" 0.0 0.0 0.0"+"\n"+
     " 0.0 0.0 0.0"+"\n"+
     " 0.0 0.0 0.0"+"\n"+
     " 0.0 0.0 0.0"+"\n"+
     " 0.0 0.0 0.0 )"+"\n\n"

    +"DATUM = NoDatum\n\n"
    +
    "UTM_ZONE = "+str(zone)+ "\n\n"
    +
    "OUTPUT_PIXEL_SIZE = 500\n"
    )
    param.close()
    return outputname



def parameter_file_mosaic(location,filename,x0,x1,y0,y1):

    param=open('param.prm','w')
    param.writelines("\n"
    +
    "INPUT_FILENAME = " + os.path.join(location,filename+'.hdf')
    + "\n\n"+
    "SPECTRAL_SUBSET = ( 1 1 0 0 0 0 )"
    + "\n\n"+
    "SPATIAL_SUBSET_TYPE = OUTPUT_PROJ_COORDS"
    + "\n\n"+
    "SPATIAL_SUBSET_UL_CORNER = ( "+str(x0)+" "+str(y0)+" )\n"
    +"SPATIAL_SUBSET_LR_CORNER = ( "+str(x1)+" "+str(y1)+" )\n"
    +"\n"+

    "OUTPUT_FILENAME ="+os.path.join(location,filename+'.tif')
    +"\n\n"+
    "RESAMPLING_TYPE = NEAREST_NEIGHBOR"
    +"\n\n"+
    "OUTPUT_PROJECTION_TYPE = "+projection
    +"\n\n"+
    "OUTPUT_PROJECTION_PARAMETERS = (\n"
     +" 0.0 0.0 0.0"+"\n"+
     " 0.0 0.0 0.0"+"\n"+
     " 0.0 0.0 0.0"+"\n"+
     " 0.0 0.0 0.0"+"\n"+
     " 0.0 0.0 0.0 )"+"\n\n"

    +"DATUM = NoDatum\n\n"
    +
    "UTM_ZONE = "+str(zone)+" \n\n"
    +
    "OUTPUT_PIXEL_SIZE = 500\n"
    )
    param.close()



def mosaicing(folder,workFolder,list_files,left_x,right_x,top_y,bottom_y,projection,zone):

    n=numpy.array(list_files)
    new_list=[]

    for i in list_files:
        select_file=i.split('.')[1][1:]
        new_list.append(select_file)

    nn=numpy.array(new_list)

    new,index=numpy.unique(nn,return_index=True)
    arcpy.gp.addMessage('Processing for....')
    for i in range(0,len(new)):
        arcpy.gp.addMessage(new[i])
        x=numpy.where(nn==new[i])
        xx=n[x].tolist()
        l=[]
        for j in range(0,len(xx)):
            l.append((xx[j]))

        f=open('mosaic.txt','w')
        f.write(' '.join(l))
        f.close()
        p=subprocess.check_call(r'start cmd /c mrtmosaic -i mosaic.txt -o '+str(new[i])+'.hdf -s \"1 1 0 0 0 0\"',shell=True)
        time.sleep(2)
        name=parameter_file_mosaic(folder,new[i],left_x,right_x,top_y,bottom_y)
        p=subprocess.check_call(r'start cmd /c resample -p param.prm',shell=True)
        time.sleep(2)

    list_Lai=glob.glob('*.Lai_1km.tif')
    list_FPAR=glob.glob('*.Fpar_1km.tif')
    lowerleft=arcpy.Point(left_x,bottom_y)
    for n in range(0,len(list_Lai)):
        name=list_Lai[n].split(".")[0]
        data_Lai=arcpy.RasterToNumPyArray(list_Lai[n],lowerleft,col,row)
        data_fpar=arcpy.RasterToNumPyArray(list_FPAR[n],lowerleft,col,row)
        data_Lai.astype('int')
        data_fpar.astype('int')
        numpy.savetxt(os.path.join(workFolder,name+'.Lai.txt'),data_Lai,fmt="%s")
        numpy.savetxt(os.path.join(workFolder,name+'.Fpar.txt'),data_fpar,fmt="%s")


INPUT_folder=sys.argv[1]
INPUT_wshed=sys.argv[2]
ischecked=sys.argv[3]
styear=sys.argv[4]
enyear=sys.argv[5]
stday=sys.argv[6]
enday=sys.argv[7]

arcpy.env.overwriteOutput=True
mxd=arcpy.mapping.MapDocument("CURRENT")
WorkDir=pathSaved(mxd.filePath)
os.chdir(WorkDir)
CreateFolder('LAI_FPAR')
workFolder=(os.path.join(WorkDir,'LAI_FPAR'))


left_x=float(arcpy.GetRasterProperties_management(INPUT_wshed,"LEFT").getOutput(0))
right_x=float(arcpy.GetRasterProperties_management(INPUT_wshed,"RIGHT").getOutput(0))
bottom_y=float(arcpy.GetRasterProperties_management(INPUT_wshed,"BOTTOM").getOutput(0))
top_y=float(arcpy.GetRasterProperties_management(INPUT_wshed,"TOP").getOutput(0))
row=float(arcpy.GetRasterProperties_management(INPUT_wshed,"ROWCOUNT").getOutput(0))
col=float(arcpy.GetRasterProperties_management(INPUT_wshed,"COLUMNCOUNT").getOutput(0))
cell_size=float(arcpy.GetRasterProperties_management(INPUT_wshed,"CELLSIZEX").getOutput(0))
spatial_ref=arcpy.Describe(INPUT_wshed).spatialReference
arcpy.gp.addMessage(left_x,top_y)
arcpy.gp.addMessage(right_x,bottom_y)
spatial_ref=arcpy.Describe(INPUT_wshed).spatialReference
os.chdir(INPUT_folder)
list_modis=glob.glob('*.hdf')

utm_zone=("{0.name}".format(spatial_ref))
zone=int((utm_zone.split("_")[-1])[:-1])
projection=utm_zone.split("_")[2]



if str(ischecked)=='true':
    arcpy.gp.addMessage('Multiple Tiles Data...')
    mosaicing(INPUT_folder,workFolder,list_modis,left_x,right_x,top_y,bottom_y,projection,zone)


elif str(ischecked)=='false':
    arcpy.gp.addMessage('Single Tile Data...')

    for i in range(0,len(list_modis)):
        name=parameter_file(INPUT_folder,list_modis[i],left_x,right_x,top_y,bottom_y,projection,zone)
        p=subprocess.check_call(r'start cmd /c resample -p param.prm',shell=True)
        time.sleep(0.5)

    list_Lai=glob.glob('*.Lai_1km.tif')
    list_FPAR=glob.glob('*.Fpar_1km.tif')
    lowerleft=arcpy.Point(left_x,bottom_y)
    for n in range(0,len(list_Lai)):
        name=list_Lai[n].split(".")[0]
        data_Lai=arcpy.RasterToNumPyArray(list_Lai[n],lowerleft,col,row)
        data_fpar=arcpy.RasterToNumPyArray(list_FPAR[n],lowerleft,col,row)
        data_Lai.astype('int')
        data_fpar.astype('int')
        numpy.savetxt(os.path.join(workFolder,name+'.Lai.txt'),data_Lai,fmt="%s")
        numpy.savetxt(os.path.join(workFolder,name+'.Fpar.txt'),data_fpar,fmt="%s")


os.chdir(workFolder)
arcpy.env.workspace=workFolder
try:
    arcpy.gp.addMessage('Generating binary file for the WEB DHM Model...')
    lai.laiconvert(col,row,int(styear),int(enyear),int(stday),int(enday))
except:
    arcpy.gp.addMessage('Error in the Input Information..Please Check and run it again...')