import arcpy
import pythonaddins,webbrowser,os
relpath=os.path.dirname(__file__)
toolPath=relpath+"\WEBDHM.tbx"

class Save(object):
    """Implementation for WEBDHMV2_addin.save (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        docs=arcpy.mapping.MapDocument('CURRENT')
        docs.save()

class about_webdhm(object):
    """Implementation for WEBDHMV2_addin.about_webdhm (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.MessageBox('WEB DHM Arc GIS Toolbox V2.0 Author : Jaya Pudashine Copyright: Tokyo University','About WEBDHM',0)
        pass

class aphrodite(object):
    """Implementation for WEBDHMV2_addin.aphrodite (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.GPToolDialog(toolPath,'aphrodite')

class bias(object):
    """Implementation for WEBDHMV2_addin.bias (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pass

class cmorph(object):
    """Implementation for WEBDHMV2_addin.cmorph (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.GPToolDialog(toolPath,'cmorph')

class down_lai(object):
    """Implementation for WEBDHMV2_addin.down_lai (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.GPToolDialog(toolPath,'downlai')

class down_land(object):
    """Implementation for WEBDHMV2_addin.down_land (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.GPToolDialog(toolPath,'downland')

class first(object):
    """Implementation for WEBDHMV2_addin.first (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.GPToolDialog(toolPath,'first')

class gpm(object):
    """Implementation for WEBDHMV2_addin.gpm (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.GPToolDialog(toolPath,'gpm')

class higher(object):
    """Implementation for WEBDHMV2_addin.higher (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.GPToolDialog(toolPath,'higher')

class hillslope(object):
    """Implementation for WEBDHMV2_addin.hillslope (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.GPToolDialog(toolPath,'hillslope')

class imerge(object):
    """Implementation for WEBDHMV2_addin.imerge (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pass

class improve(object):
    """Implementation for WEBDHMV2_addin.improve (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        webbrowser.open_new('https://github.com/jayapudashine')

class lai_process(object):
    """Implementation for WEBDHMV2_addin.lai_process (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.GPToolDialog(toolPath,'laiprocess')

class land_process(object):
    """Implementation for WEBDHMV2_addin.land_process (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.GPToolDialog(toolPath,'landprocess')

class manual(object):
    """Implementation for WEBDHMV2_addin.manual (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        webbrowser.open_new(r'file://'+relpath+'\help_webdhm.pdf')
        
class nasa(object):
    """Implementation for WEBDHMV2_addin.nasa (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.GPToolDialog(toolPath,'nasa')

class observed(object):
    """Implementation for WEBDHMV2_addin.observed (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.GPToolDialog(toolPath,'observed')

class preprocess(object):
    """Implementation for WEBDHMV2_addin.preprocess (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.GPToolDialog(toolPath,'preprocess')

class process_basin(object):
    """Implementation for WEBDHMV2_addin.process_basin (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.GPToolDialog(toolPath,'processbasin')

class process_gpm(object):
    """Implementation for WEBDHMV2_addin.process_gpm (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pass

class process_imerge(object):
    """Implementation for WEBDHMV2_addin.process_imerge (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pass

class soil_process(object):
    """Implementation for WEBDHMV2_addin.soil_process (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.GPToolDialog(toolPath,'soilprocess')

class trmm(object):
    """Implementation for WEBDHMV2_addin.trmm (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.GPToolDialog(toolPath,'trmm')

class utm(object):
    """Implementation for WEBDHMV2_addin.utm (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.GPToolDialog(toolPath,'utm')

class watershed(object):
    """Implementation for WEBDHMV2_addin.watershed (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.GPToolDialog(toolPath,'watershed')