import os,webbrowser

new=2

region_input=arcpy.GetParameterAsText(0)

if region_input=='North America':
    url="http://edc2.usgs.gov/glcc/tablambert_na.php"

elif region_input=='South America':
    url="http://edc2.usgs.gov/glcc/tablambert_sa.php"

elif region_input=='Eurasia':
    url="http://edc2.usgs.gov/glcc/tablambert_euras_eur.php"

elif region_input=='Australia Pacific':
    url='http://edc2.usgs.gov/glcc/tablambert_ausipac.php'

elif region_input=='Africa':
    url='http://edc2.usgs.gov/glcc/tablambert_af.php'

webbrowser.open(url,new=new)

