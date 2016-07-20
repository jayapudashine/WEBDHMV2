import sys,os,csv,glob,zipfile,shutil,numpy,arcpy
import numpy as np
import linecache
from arcpy.sa import *
from arcpy import env
import tempfile
arcpy.CheckOutExtension("Spatial")


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


def readASCI(fileName):
        line=[]
        for i in range(1,7):
            line.append(linecache.getline(fileName,i))

        ncol=int(line[0].split()[1])
        nrow=int(line[1].split()[1])
        xl=float(line[2].split()[1])
        yl=float(line[3].split()[1])
        cell_size=int(line[4].split()[1])
        no_data=float(line[5].split()[1])
        print fileName,ncol,nrow,no_data
        data=np.genfromtxt(fileName,skiprows=6)
        data_new=np.around(data,decimals=5)
        return data_new,nrow,ncol,no_data


def main():

    folder=sys.argv[1]
    watershed=sys.argv[2]
    mxd=arcpy.mapping.MapDocument("CURRENT")
    path=pathSaved(mxd.filePath)
    os.chdir(folder)
    check_list=glob.glob('*.asc')
    file_list=['alpha.asc','ks.asc','soil_depth.asc','soil_unit.asc','thetar.asc','thetas.asc','watern.asc']
    status=cmp(sorted(file_list),sorted(check_list))
    row=float(arcpy.GetRasterProperties_management(watershed,"ROWCOUNT").getOutput(0))
    col=float(arcpy.GetRasterProperties_management(watershed,"COLUMNCOUNT").getOutput(0))

    if int(status)>=0:
        os.chdir(path)
        spatial_ref=arcpy.Describe(Raster(watershed)).spatialReference
        cell_size=arcpy.GetRasterProperties_management(watershed,"CELLSIZEX")
        CreateFolder('soil')
        new_path=os.path.join(path,'soil')
        os.chdir(new_path)
        env.overwriteOutput=True
        env.workspace=new_path
        coordinateSystem = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
        CreateFolder('temp_soil')
        temp_dir=os.path.join(new_path,'temp_soil')
        arcpy.gp.addMessage('Processing For..')
        for i in range(0,len(check_list)):
            arcpy.gp.addMessage(check_list[i])
            env.workspace=temp_dir

            if check_list[i]=='soil_unit.asc':
                arcpy.gp.addMessage('True')
                arcpy.ASCIIToRaster_conversion(os.path.join(folder,check_list[i]),"temp_ascfile",'INTEGER')
            else:
                arcpy.ASCIIToRaster_conversion(os.path.join(folder,check_list[i]),"temp_ascfile",'FLOAT')

            arcpy.DefineProjection_management("temp_ascfile",coordinateSystem)
            arcpy.ProjectRaster_management(watershed,'temp_wshd',coordinateSystem)
            env.extent='temp_wshd'
            arcpy.ProjectRaster_management("temp_ascfile",'Proj_asc',spatial_ref,'NEAREST',cell_size)
            env.extent=watershed
            temp_proj=ExtractByMask('Proj_asc',watershed)
            arcpy.RasterToASCII_conversion(temp_proj,os.path.join(new_path,check_list[i]))
            del temp_proj


        env.workspace=new_path
        DeleteFile(new_path,['temp_soil'])

        arcpy.gp.addMessage('Creating files for WEBDHM Model....')
        os.chdir(new_path)
        code,nrow,ncol,no_data=readASCI('soil_unit.asc')
        thetas=readASCI('thetas.asc')[0]
        thetar=readASCI('thetar.asc')[0]
        alpha=readASCI('alpha.asc')[0]
        ks=readASCI('ks.asc')[0]
        watern=readASCI('watern.asc')[0]


        unit=[]
        a=[]
        ts=[]
        tr=[]
        k=[]
        wn=[]
        n=0
        arcpy.gp.addMessage(row)
        arcpy.gp.addMessage(col)
        for i in range(0,int(row)):
            for  j in range(0,int(col)):
                if code[i,j]!=-9999:
                    key=0


                    for m in range(0,n):
                        if(code[i,j]==unit[m] and alpha[i,j]==a[m] and thetar[i,j]==tr[m] and thetas[i,j]==ts[m] and ks[i,j]==k[m] and watern[i,j]==wn[m]):
                            key=1

                    if key==0:

                        unit.append(code[i,j])
                        a.append(alpha[i,j])
                        ts.append(thetas[i,j])
                        tr.append(thetar[i,j])
                        k.append(ks[i,j])
                        wn.append(watern[i,j])
                        n=n+1


        for i in range(0,len(unit)):
            number=0
            for j in range(0,len(unit)):
                if(unit[i]==unit[j] and a[i]!=a[j]):
                    number=number+1

            if number>1:
                print number

        f=open('soil_water_para.dat','w')
        f.write("Soil water parameters \n\"soil_code,\"\n\"theta_s,\"\t\"theta_r,\"\t\"alpha,\"\t\"ks1,\"\t\"ks2,\"\t\"ksg,\"\t\"GWcs,\"\t\"apow,\"\t\"bpow,\"\t\"lamdaf_max,\"\tvlcmin\n")


        for i in range(0,len(unit)):
            k[i]=k[i]*10/24
            f.write(str(int(unit[i]))+'\n\t\t'+str(ts[i])+'\t'+str(tr[i])+'\t'+str(a[i])+'\t'+str(wn[i])+'\t'+str(k[i])+'\t'+str(0.1*k[i])+'\t'+str(0.05*k[i])+'\t-9999\t-9999\t-9999\t-9999\n')

        f.close()

        soil_unit=open('soil_code.txt','w')
        soil_unit.writelines('Record'+'\t'+'VALUE'+'\t'+'COUNT'+'\n')
        x_new=code.ravel()
        x_mask=np.where(x_new[:]!=no_data)[0]
        x_data=x_new[x_mask].astype(int)
        unique,counts=np.unique(x_data,return_counts=True)
        xn=np.asarray((unique,counts)).T
        xn=xn.astype(int)
        for j in range(0,len(unique)):
            soil_unit.writelines(str(j+1)+'\t'+str(unique[j])+'\t'+str(counts[j])+'\n')


        soil_unit.close()


    else:
        arcpy.gp.addMessage('Some Files are Missing.. Please Check whether all files are stored in the folder or not and re-run it again.')



if __name__ == "__main__":
    try:
        main()
    except Exception, e:
        import gc
        gc.collect()
        import traceback
        arcpy.AddError(traceback.format_exc())









