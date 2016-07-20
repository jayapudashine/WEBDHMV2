#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Jaya
#
# Created:     19/06/2016
# Copyright:   (c) Jaya 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from ftplib import FTP
from datetime import timedelta
from datetime import datetime
import re
import os
import arcpy
import shutil



def CreateFolder(folderName):

    if os.path.isdir(folderName)==True:
        shutil.rmtree(folderName)
        os.mkdir(folderName)
    else:
        os.mkdir(folderName)


start_date=arcpy.GetParameterAsText(0)
end_date=arcpy.GetParameterAsText(1)
file_path=arcpy.GetParameterAsText(2)
os.chdir(file_path)
CreateFolder('gpm_rainfall')
outpath=os.path.join(file_path,'gpm_rainfall')
arcpy.gp.addMessage(outpath)
st_date=datetime.strptime(start_date,'%m/%d/%Y')
en_date=datetime.strptime(end_date,'%m/%d/%Y')

url = "jsimpson.pps.eosdis.nasa.gov"
ftp = FTP(url)

ftp.login('letterjaya@gmail.com', 'letterjaya@gmail.com')


for dt in [st_date + timedelta(t) for t in range((en_date - st_date).days+1)]:

    try:
        ftp.cwd("/data/imerg/gis/{0}/{1:02d}".format(dt.year, dt.month))
        filenames = [f for f in ftp.nlst() if re.match(r"3B.*{0}.*S000000.*1day\.tif.*".format(dt.strftime("%Y%m%d")), f) is not None]
        if len(filenames) > 0:
                fname = filenames[0]
                arcpy.gp.addMessage(fname)
                with open("{0}/{1}".format(outpath, fname), 'wb') as f:
                    ftp.retrbinary("RETR {0}".format(fname), f.write)

    except Exception:
        print "WARNING"
