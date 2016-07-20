import subprocess,os

os.chdir('C:\\Users\\Jaya_HOME\\Desktop\\modis')

p=subprocess.Popen(r'start cmd /c mrtmosaic -i mosaicinput.txt -o mosaic_temp.hdf',shell=True)
p.wait()

