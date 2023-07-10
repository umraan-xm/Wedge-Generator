from PySide2.QtWidgets import *
from PySide2.QtCore import *


def createOverlayText(topnet):
    ropcomposite = topnet.createNode('ropcomposite')
    
    parms = ropcomposite.parmTemplateGroup()
    overlay_folder = hou.FolderParmTemplate('overlay', "Overlay")
    overlaytext = hou.StringParmTemplate('overlaytext', "Text", 1)
    overlaytext.setTags({'editor': '1', 'editorlines': '8-40'})
    overlay_folder.addParmTemplate(overlaytext)
    parms.append(overlay_folder)
    
    ropcomposite.setParmTemplateGroup(parms)
    ropcomposite.parm('overlaytext').set("Overlay $F")
    
    cop = ropcomposite.children()[2]
    file_pdg_result = cop.children()[0]
    
    font = cop.createNode('font')
    font.parm('font').set('Lato')
    font.parm('textsize').set(30)
    font.parm('text').set(ropcomposite.parm('overlaytext'))
    font.parm('halign').set(0)
    font.parm('valign').set(3)
    font.parm('translate1').set(-0.45)
    font.parm('translate2').set(-0.45)
    font.parm('addplanes').set(0)
    font.setFirstInput(file_pdg_result)
    
    dropshadow = cop.createNode('dropshadow')
    dropshadow.setFirstInput(font)
    
    over = cop.createNode('over')
    over.setFirstInput(dropshadow)
    over.setNextInput(file_pdg_result)
    over.setGenericFlag(hou.nodeFlag.Render, 1)
    
    cop.layoutChildren()
    
    return ropcomposite
        

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        #self.setMinimumSize(500, 500)
        
        self.lbl_wedge_attrib = None
        self.txt_wedge_attrib = None
        self.lbl_geometry_path = None
        self.txt_geometry_path = None
        self.lbl_frame_range = None
        self.txt_startframe = None
        self.txt_endframe = None
        self.btn_create = None
        self.lyt_main = None
        self.lyt_wedge_attrib = None
        self.lyt_geometry_path = None
        self.lyt_frame_range = None
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        
    def create_widgets(self):
        self.lbl_wedge_attrib = QLabel("Wedge Attribute Name: ")
        self.txt_wedge_attrib = QLineEdit()
        
        self.lbl_geometry_path = QLabel("Sim Geometry Node:      ")
        self.txt_geometry_path = QLineEdit()
        
        self.lbl_frame_range = QLabel("Frame Range: ")
        self.txt_startframe = QLineEdit()
        self.txt_endframe = QLineEdit()
        
        self.btn_create = QPushButton("Create")
        
    def create_layouts(self):
        self.lyt_main = QVBoxLayout()
        self.lyt_wedge_attrib = QHBoxLayout()
        self.lyt_geometry_path = QHBoxLayout()
        self.lyt_frame_range = QHBoxLayout()
        
        self.lyt_wedge_attrib.addWidget(self.lbl_wedge_attrib)
        self.lyt_wedge_attrib.addWidget(self.txt_wedge_attrib)
        
        self.lyt_geometry_path.addWidget(self.lbl_geometry_path)
        self.lyt_geometry_path.addWidget(self.txt_geometry_path)
        
        self.lyt_frame_range.addWidget(self.lbl_frame_range)
        self.lyt_frame_range.addWidget(self.txt_startframe)
        self.lyt_frame_range.addWidget(self.txt_endframe)
        
        self.lyt_main.addLayout(self.lyt_wedge_attrib)
        self.lyt_main.addLayout(self.lyt_geometry_path)
        self.lyt_main.addLayout(self.lyt_frame_range)
        self.lyt_main.addStretch(1)
        self.lyt_main.addWidget(self.btn_create)
        
        self.setLayout(self.lyt_main)
        
    def create_connections(self):
        self.btn_create.clicked.connect(self.create)
        
    def create(self):
        wedge_attrib_name = self.txt_wedge_attrib.text()
        geometry_path = self.txt_geometry_path.text()
        startframe = self.txt_startframe.text()
        endframe = self.txt_endframe.text()
    
        topnet = hou.node('/obj').createNode('topnet')
        
        wedge = topnet.createNode('wedge')
        wedge.parm('wedgeattributes').set(1)
        wedge.parm('name1').set(wedge_attrib_name)
        
        geometry = hou.node(geometry_path)
        if geometry:
            rop_geometry_pdg = hou.node(geometry_path).createNode('rop_geometry')
        else:
            hou.ui.displayMessage("Invalid path for geometry path. Creating template geoemtry node for rop_geometry.")
            rop_geometry_pdg = hou.node('/obj').createNode('geo').createNode('rop_geometry')
        rop_geometry_pdg.parm('sopoutput').set("$JOB/pdg/`@wedgeattribs`/sim/w`@wedgeindex`/wedge.$F.bgeo.sc")
        
        
        ropfetch_sim = topnet.createNode('ropfetch')
        ropfetch_sim.parm('framegeneration').set(1)
        ropfetch_sim.parm('batchall').set(1)
        if startframe:
            ropfetch_sim.parm('range1').deleteAllKeyframes()
            ropfetch_sim.parm('range1').set(int(startframe))
        if endframe: 
            ropfetch_sim.parm('range2').deleteAllKeyframes()
            ropfetch_sim.parm('range2').set(int(endframe))
        ropfetch_sim.parm('roppath').set(rop_geometry_pdg.path())
        ropfetch_sim.setFirstInput(wedge)
        
        camera_pdg = hou.node('/obj').createNode('cam', node_name='pdg')
        opengl = topnet.createNode('ropnet').createNode('opengl')
        opengl.parm('camera').set(camera_pdg.path())
        opengl.parm('forceobjects').set(geometry_path)
        opengl.parm('picture').set("$JOB/pdg/`@wedgeattribs`/render/w`@wedgeindex`/wedge.$F.bgeo.sc")
        
        
        ropfetch_render = topnet.createNode('ropfetch')
        ropfetch_render.parm('batchall').set(1)
        ropfetch_render.parm('roppath').set(opengl.path())
        ropfetch_render.setFirstInput(ropfetch_sim)
        
        overlaytext = createOverlayText(topnet)
        overlaytext.parm('copoutput').set("$JOB/pdg/`@wedgeattribs`/overlay/w`@wedgeindex`/wedge.$F.png")
        overlaytext.parm('batchall').set(1)
        overlaytext.parm('overlaytext').set(f"`@wedgeattribs`: `@{wedge_attrib_name}`")
        overlaytext.setFirstInput(ropfetch_render)
        
        partitionbyframe = topnet.createNode('partitionbyframe')
        partitionbyframe.setFirstInput(overlaytext)
        
        imagemagick = topnet.createNode('imagemagick')
        imagemagick.parm('outputfilepath').set("$JOB/pdg/`@wedgeattribs`/montage/w`@wedgeindex`/wedge.$F.png")
        imagemagick.setFirstInput(partitionbyframe)
        
        waitforall = topnet.createNode('waitforall')
        waitforall.setFirstInput(imagemagick)
        
        ffmpeg = topnet.createNode('ffmpegencodevideo')
        ffmpeg.parm('framelistfile').set("$JOB/pdg/`@wedgeattribs`/`@pdg_index`_framelist.txt")
        ffmpeg.parm('outputfilepath').set("$JOB/pdg/`@wedgeattribs`/`@wedgeattribs`.mp4")
        ffmpeg.setFirstInput(waitforall)
        
        topnet.layoutChildren()
        self.close()

window = MainWindow()
window.show()