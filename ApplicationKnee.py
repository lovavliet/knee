import vtk
import sys
import time

# Function to create a volume render with as input the scalars, colors, opacity and piecewise function
def createVolumeRender(File, ScalarList, ColorList, OpacList, PieceList):
  #Create the mappers
  volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
  volumeMapper.SetInputConnection(File.GetOutputPort())
  volumeMapper.SetBlendModeToComposite()

  #Create the color transfer function
  volumeCTF = vtk.vtkColorTransferFunction()
  volumeCTF.AddRGBPoint(ScalarList[0],  ColorList[0][0], ColorList[0][1], ColorList[0][2])
  volumeCTF.AddRGBPoint(ScalarList[1],  ColorList[1][0], ColorList[1][1], ColorList[1][2])
  volumeCTF.AddRGBPoint(ScalarList[2],  ColorList[2][0], ColorList[2][1], ColorList[2][2])
  volumeCTF.AddRGBPoint(ScalarList[3],  ColorList[3][0], ColorList[3][1], ColorList[3][2])

  #Create the piecewise function for opacity function
  volumeOTF = vtk.vtkPiecewiseFunction()
  volumeOTF.AddPoint(ScalarList[0],  OpacList[0])
  volumeOTF.AddPoint(ScalarList[1],  OpacList[1])
  volumeOTF.AddPoint(ScalarList[2],  OpacList[2])
  volumeOTF.AddPoint(ScalarList[3],  OpacList[3])

  #Create the piecewise function for internal opacity function
  volumeGOTF = vtk.vtkPiecewiseFunction()
  volumeGOTF.AddPoint(0,   PieceList[0])
  volumeGOTF.AddPoint(90,  PieceList[1])
  volumeGOTF.AddPoint(100, PieceList[2])

  #Add all the function and ambient, diffuse and specular to the volume property
  volumeProperty = vtk.vtkVolumeProperty()
  volumeProperty.SetColor(volumeCTF)
  volumeProperty.SetScalarOpacity(volumeOTF)
  volumeProperty.SetGradientOpacity(volumeGOTF)
  volumeProperty.SetInterpolationTypeToLinear()
  volumeProperty.ShadeOn()
  volumeProperty.SetAmbient(0.5)
  volumeProperty.SetDiffuse(0.5)
  volumeProperty.SetSpecular(0.5)

  #Create volume and set mapper and property to volume
  volume = vtk.vtkVolume()
  volume.SetMapper(volumeMapper)
  volume.SetProperty(volumeProperty)

  #Return volume
  return volume

# Function to create a isosurface actor with the threshold value and smoothing iterations as input
def createKneeSkin(reader, value, smooth):
  #Function to select tissue at a threshold
  selectTissue = vtk.vtkImageThreshold()
  selectTissue.ThresholdBetween(5, 1150)
  selectTissue.SetInValue(255)
  selectTissue.SetOutValue(0)
  selectTissue.SetInputConnection(reader.GetOutputPort())

  #Gaussian function for marching cubes
  gaussianRadius = 1
  gaussianStandardDeviation = 2.0
  gaussian = vtk.vtkImageGaussianSmooth()
  gaussian.SetStandardDeviations(gaussianStandardDeviation, gaussianStandardDeviation, gaussianStandardDeviation)
  gaussian.SetRadiusFactors(gaussianRadius, gaussianRadius, gaussianRadius)
  gaussian.SetInputConnection(selectTissue.GetOutputPort())

  #Marching cubes algorithm
  isoValue = value
  mcubes = vtk.vtkMarchingCubes()
  mcubes.SetInputConnection(gaussian.GetOutputPort())
  mcubes.ComputeScalarsOff()
  mcubes.ComputeGradientsOff()
  mcubes.ComputeNormalsOff()
  mcubes.SetValue(0, isoValue)

  #Smoothing function
  smoothingIterations = smooth
  passBand = 0.001
  featureAngle = 90
  smoother = vtk.vtkWindowedSincPolyDataFilter()
  smoother.SetInputConnection(mcubes.GetOutputPort())
  smoother.SetNumberOfIterations(smoothingIterations)
  smoother.BoundarySmoothingOn()
  smoother.FeatureEdgeSmoothingOn()
  smoother.SetFeatureAngle(featureAngle)
  smoother.SetPassBand(passBand)
  smoother.NonManifoldSmoothingOff()
  smoother.NormalizeCoordinatesOn()
  smoother.Update()

  #Function for vtk poly data normals
  normals = vtk.vtkPolyDataNormals()
  normals.SetInputConnection(smoother.GetOutputPort())
  normals.SetFeatureAngle(featureAngle)

  #Function for vtk stripper
  stripper = vtk.vtkStripper()
  stripper.SetInputConnection(normals.GetOutputPort())

  #Function for vtk mapper
  mapper = vtk.vtkPolyDataMapper()
  mapper.SetInputConnection(stripper.GetOutputPort())

  #Create actor
  actor = vtk.vtkActor()
  actor.SetMapper(mapper)

  #Return actor
  return actor

# Class for the interaction with the keyboard
class MyInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self,parent=None):
        self.parent = iren
        self.AddObserver("KeyPressEvent",self.keyPressEvent)

    #On press of spacebar, loop through all time steps
    def keyPressEvent(self,obj,event):
      key = self.parent.GetKeySym()
      if key == 'space':
        text_widget.Off()
        for i in range(len(muscle_list1)):
          skin.SetFileName("Structures/"+skin_list[i])
          bones.SetFileName("Structures/"+bone_list[i])
          muscle1.SetFileName("Structures/"+muscle_list1[i])
          muscle2.SetFileName("Structures/"+muscle_list2[i])
          ligament1.SetFileName("Structures/"+ligament1_list[i])
          ligament2.SetFileName("Structures/"+ligament2_list[i])
          tendon1.SetFileName("Structures/"+tendon1_list[i])
          tendon2.SetFileName("Structures/"+tendon2_list[i])
          menis.SetFileName("Structures/"+menis_list[i])
          iren.GetRenderWindow().Render()

# Slider created for the flexion of the Knee
class SliderFlexion():
  #Initialize all anantomic structures
    def __init__(self, skin, bones, muscle1, muscle2, ligament1, ligament2, tendon1, tendon2, meniscus):
        self.skin = skin
        self.bones = bones
        self.muscle1 = muscle1
        self.muscle2 = muscle2
        self.ligament1 = ligament1
        self.ligament2 = ligament2
        self.tendon1 = tendon1
        self.tendon2 = tendon2
        self.meniscus  = meniscus
    #Depended on the value of the slider, visualize a time step
    def __call__(self, caller, ev):
        sliderWidget = caller
        value = sliderWidget.GetRepresentation().GetValue()
        if value >= 0 and value < 1:
          self.skin.SetFileName("Structures/"+skin_list[0])
          self.bones.SetFileName("Structures/"+bone_list[0])
          self.muscle1.SetFileName("Structures/"+muscle_list1[0])
          self.muscle2.SetFileName("Structures/"+muscle_list2[0])
          self.ligament1.SetFileName("Structures/"+ligament1_list[0])
          self.ligament2.SetFileName("Structures/"+ligament2_list[0])
          self.tendon1.SetFileName("Structures/"+tendon1_list[0])
          self.tendon2.SetFileName("Structures/"+tendon2_list[0])
          self.meniscus.SetFileName("Structures/"+menis_list[0])

        elif value >= 1 and value < 2:
          self.skin.SetFileName("Structures/"+skin_list[1])
          self.bones.SetFileName("Structures/"+bone_list[1])
          self.muscle1.SetFileName("Structures/"+muscle_list1[1])
          self.muscle2.SetFileName("Structures/"+muscle_list2[1])
          self.ligament1.SetFileName("Structures/"+ligament1_list[1])
          self.ligament2.SetFileName("Structures/"+ligament2_list[1])
          self.tendon1.SetFileName("Structures/"+tendon1_list[1])
          self.tendon2.SetFileName("Structures/"+tendon2_list[1])
          self.meniscus.SetFileName("Structures/"+menis_list[1])

        elif value >= 2 and value < 3:
          self.skin.SetFileName("Structures/"+skin_list[2])
          self.bones.SetFileName("Structures/"+bone_list[2])
          self.muscle1.SetFileName("Structures/"+muscle_list1[2])
          self.muscle2.SetFileName("Structures/"+muscle_list2[2])
          self.ligament1.SetFileName("Structures/"+ligament1_list[2])
          self.ligament2.SetFileName("Structures/"+ligament2_list[2])
          self.tendon1.SetFileName("Structures/"+tendon1_list[2])
          self.tendon2.SetFileName("Structures/"+tendon2_list[2])
          self.meniscus.SetFileName("Structures/"+menis_list[2])

        elif value >= 3 and value < 4:
          self.skin.SetFileName("Structures/"+skin_list[3])
          self.bones.SetFileName("Structures/"+bone_list[3])
          self.muscle1.SetFileName("Structures/"+muscle_list1[3])
          self.muscle2.SetFileName("Structures/"+muscle_list2[3])
          self.ligament1.SetFileName("Structures/"+ligament1_list[3])
          self.ligament2.SetFileName("Structures/"+ligament2_list[3])
          self.tendon1.SetFileName("Structures/"+tendon1_list[3])
          self.tendon2.SetFileName("Structures/"+tendon2_list[3])
          self.meniscus.SetFileName("Structures/"+menis_list[3])

        elif value >= 4 and value < 5:
          self.skin.SetFileName("Structures/"+skin_list[4])
          self.bones.SetFileName("Structures/"+bone_list[4])
          self.muscle1.SetFileName("Structures/"+muscle_list1[4])
          self.muscle2.SetFileName("Structures/"+muscle_list2[4])
          self.ligament1.SetFileName("Structures/"+ligament1_list[4])
          self.ligament2.SetFileName("Structures/"+ligament2_list[4])
          self.tendon1.SetFileName("Structures/"+tendon1_list[4])
          self.tendon2.SetFileName("Structures/"+tendon2_list[4])
          self.meniscus.SetFileName("Structures/"+menis_list[4])

        elif value >= 5 and value < 6:
          self.skin.SetFileName("Structures/"+skin_list[5])
          self.bones.SetFileName("Structures/"+bone_list[5])
          self.muscle1.SetFileName("Structures/"+muscle_list1[5])
          self.muscle2.SetFileName("Structures/"+muscle_list2[5])
          self.ligament1.SetFileName("Structures/"+ligament1_list[5])
          self.ligament2.SetFileName("Structures/"+ligament2_list[5])
          self.tendon1.SetFileName("Structures/"+tendon1_list[5])
          self.tendon2.SetFileName("Structures/"+tendon2_list[5])
          self.meniscus.SetFileName("Structures/"+menis_list[5])

        elif value >= 6 and value < 7:
          self.skin.SetFileName("Structures/"+skin_list[6])
          self.bones.SetFileName("Structures/"+bone_list[6])
          self.muscle1.SetFileName("Structures/"+muscle_list1[6])
          self.muscle2.SetFileName("Structures/"+muscle_list2[6])
          self.ligament1.SetFileName("Structures/"+ligament1_list[6])
          self.ligament2.SetFileName("Structures/"+ligament2_list[6])
          self.tendon1.SetFileName("Structures/"+tendon1_list[6])
          self.tendon2.SetFileName("Structures/"+tendon2_list[6])
          self.meniscus.SetFileName("Structures/"+menis_list[6])

# Slider created for the opacity of the Skin
class SliderOpacity():
    #Initialize the scalar values
    def __init__(self, scalar):
        self.scalar = scalar
    def __call__(self, caller, ev):
      sliderWidget = caller
      value = sliderWidget.GetRepresentation().GetValue()
      if value >= 0 and value < 100:
        #Change opacity isosurface
        skinActor.GetProperty().SetOpacity(value/100)
        #Change opacity of volume render
        volumeOTF = vtk.vtkPiecewiseFunction()
        volumeOTF.AddPoint(self.scalar[0],  0)
        volumeOTF.AddPoint(self.scalar[1],  value/200)
        volumeOTF.AddPoint(self.scalar[2],  value/200)
        volumeOTF.AddPoint(self.scalar[3],  0)
        volumeSkin.GetProperty().SetScalarOpacity(volumeOTF)
        #Render
        renWin.Render()

# Slider created for the opacity of the Bone
class BoneOpacity():
    #Initialize the scalar values
    def __init__(self, scalar):
        self.scalar = scalar
    def __call__(self, caller, ev):
      sliderWidget = caller
      value = sliderWidget.GetRepresentation().GetValue()
      if value >= 0 and value < 100:
        #Change opacity isosurface
        boneActor.GetProperty().SetOpacity(value/100)
        #Change opacity of volume render
        volumeOTF = vtk.vtkPiecewiseFunction()
        volumeOTF.AddPoint(self.scalar[0],  0)
        volumeOTF.AddPoint(self.scalar[1],  value/200)
        volumeOTF.AddPoint(self.scalar[2],  value/200)
        volumeOTF.AddPoint(self.scalar[3],  0)
        volumeBone.GetProperty().SetScalarOpacity(volumeOTF)
        #Render
        renWin.Render()

# Slider created for the opacity of the Tendon
class TendonOpacity():
    #Initialize the scalar values
    def __init__(self, scalar):
        self.scalar = scalar
    def __call__(self, caller, ev):
      sliderWidget = caller
      value = sliderWidget.GetRepresentation().GetValue()
      if value >= 0 and value < 100:
        #Change opacity isosurface
        tendon1Actor.GetProperty().SetOpacity(value/100)
        tendon2Actor.GetProperty().SetOpacity(value/100)
        #Change opacity of volume render
        volumeOTF = vtk.vtkPiecewiseFunction()
        volumeOTF.AddPoint(self.scalar[0],  0)
        volumeOTF.AddPoint(self.scalar[1],  value/200)
        volumeOTF.AddPoint(self.scalar[2],  value/200)
        volumeOTF.AddPoint(self.scalar[3],  0)
        volumeTendon1.GetProperty().SetScalarOpacity(volumeOTF)
        volumeTendon2.GetProperty().SetScalarOpacity(volumeOTF)
        #Render
        renWin.Render()

# Slider created for the opacity of the Ligament
class LigamentOpacity():
    #Initialize the scalar values
    def __init__(self, scalar):
        self.scalar = scalar
    def __call__(self, caller, ev):
      sliderWidget = caller
      value = sliderWidget.GetRepresentation().GetValue()
      if value >= 0 and value < 100:
        #Change opacity isosurface
        ligament1Actor.GetProperty().SetOpacity(value/100)
        ligament2Actor.GetProperty().SetOpacity(value/100)
        #Change opacity of volume render
        volumeOTF = vtk.vtkPiecewiseFunction()
        volumeOTF.AddPoint(self.scalar[0],  0)
        volumeOTF.AddPoint(self.scalar[1],  value/200)
        volumeOTF.AddPoint(self.scalar[2],  value/200)
        volumeOTF.AddPoint(self.scalar[3],  0)
        volumeLigament1.GetProperty().SetScalarOpacity(volumeOTF)
        volumeLigament2.GetProperty().SetScalarOpacity(volumeOTF)
        #Render
        renWin.Render()

# Slider created for the opacity of the Meniscus
class MeniscusOpacity():
    #Initialize the scalar values
    def __init__(self, scalar):
        self.scalar = scalar
    def __call__(self, caller, ev):
      sliderWidget = caller
      value = sliderWidget.GetRepresentation().GetValue()
      if value >= 0 and value < 100:
        #Change opacity isosurface
        menisActor.GetProperty().SetOpacity(value/100)
        #Change opacity of volume render
        volumeOTF = vtk.vtkPiecewiseFunction()
        volumeOTF.AddPoint(self.scalar[0],  0)
        volumeOTF.AddPoint(self.scalar[1],  value/200)
        volumeOTF.AddPoint(self.scalar[2],  value/200)
        volumeOTF.AddPoint(self.scalar[3],  0)
        volumeMenis2.GetProperty().SetScalarOpacity(volumeOTF)
        volumeMenis2.GetProperty().SetScalarOpacity(volumeOTF)
        #Render
        renWin.Render()

# Slider created for the opacity of the Muscles
class MuscleOpacity():
    #Initialize the scalar values
    def __init__(self, scalar):
        self.scalar = scalar

    def __call__(self, caller, ev):
      sliderWidget = caller
      value = sliderWidget.GetRepresentation().GetValue()
      if value >= 0 and value < 100:
        #Change opacity isosurface
        muscleActor1.GetProperty().SetOpacity(value/100)
        muscleActor2.GetProperty().SetOpacity(value/100)
        #Change opacity of volume render
        volumeOTF = vtk.vtkPiecewiseFunction()
        volumeOTF.AddPoint(self.scalar[0],  0)
        volumeOTF.AddPoint(self.scalar[1],  value/200)
        volumeOTF.AddPoint(self.scalar[2],  value/200)
        volumeOTF.AddPoint(self.scalar[3],  0)
        volumeMuscle1.GetProperty().SetScalarOpacity(volumeOTF)
        volumeMuscle2.GetProperty().SetScalarOpacity(volumeOTF)
        #Render
        renWin.Render()

# Slider created to change the render style from Isosurface to Volume rendering or vice versa
class ChangeRenderStyle():
    def __init__(self, muscle):
      self.muscle = muscle
    def __call__(self, caller, ev):
      sliderWidget = caller
      value = sliderWidget.GetRepresentation().GetValue()
      #If value of slider above 0.5 then change to Volume Rendering
      if value >= 0.5:
        ren.RemoveActor(boneActor)
        ren.RemoveActor(skinActor)
        ren.RemoveActor(muscleActor1)
        ren.RemoveActor(muscleActor2)
        ren.RemoveActor(ligament1Actor)
        ren.RemoveActor(ligament2Actor)
        ren.RemoveActor(tendon1Actor)
        ren.RemoveActor(tendon2Actor)
        ren.RemoveActor(menisActor)
        ren.AddActor(volumeBone)
        ren.AddActor(volumeLigament1)
        ren.AddActor(volumeLigament2)
        ren.AddActor(volumeMenis)
        ren.AddActor(volumeMuscle1)
        ren.AddActor(volumeMuscle2)
        ren.AddActor(volumeTendon1)
        ren.AddActor(volumeTendon2)
        ren.AddActor(volumeSkin)
      #If value of slider under 0.5 then change to Isosurface rendering
      elif value < 0.5:
        ren.RemoveActor(volumeBone)
        ren.RemoveActor(volumeSkin)
        ren.RemoveActor(volumeMuscle1)
        ren.RemoveActor(volumeMuscle2)
        ren.RemoveActor(volumeLigament1)
        ren.RemoveActor(volumeLigament2)
        ren.RemoveActor(volumeTendon1)
        ren.RemoveActor(volumeTendon2)
        ren.RemoveActor(volumeMenis)
        ren.AddActor(ligament1Actor)
        ren.AddActor(ligament2Actor)
        ren.AddActor(boneActor)
        ren.AddActor(muscleActor1)
        ren.AddActor(muscleActor2)
        ren.AddActor(tendon2Actor)
        ren.AddActor(tendon1Actor)
        ren.AddActor(menisActor)
        ren.AddActor(skinActor)

# Function to create sliders easier
# Input are max and min of slider, current value. Point1 and Point2 are coordinates of the endings of the slider.
# Title is a string for title of the slider and dimensions are the tube width/slider length/title height/label height of slider.
def createSliderStyle(min,max,value,point1,point2,title,dim):
  SliderStyle = vtk.vtkSliderRepresentation2D()
  # Set max/min/value and title
  SliderStyle.SetMinimumValue(min)
  SliderStyle.SetMaximumValue(max)
  SliderStyle.SetValue(value)
  SliderStyle.SetTitleText(title)
  #Set the coordinates of the endings
  SliderStyle.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
  SliderStyle.GetPoint1Coordinate().SetValue(point1[0], point1[1])
  SliderStyle.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
  SliderStyle.GetPoint2Coordinate().SetValue(point2[0], point2[1])
  #Set the dimensions of the slider
  SliderStyle.SetTubeWidth(dim[0])
  SliderStyle.SetSliderLength(dim[1])
  SliderStyle.SetTitleHeight(dim[2])
  SliderStyle.SetLabelHeight(dim[3])
  return SliderStyle


#List of all anatomic structures for different time steps
skin_list       = ['skin_1.vti','skin_2.vti','skin_3.vti','skin_4.vti','skin_5.vti','skin_6.vti','skin_7.vti']
bone_list       = ['bone1.vti','bone2.vti','bone3.vti','bone4.vti','bone5.vti','bone6.vti','bone7.vti']
muscle_list1    = ['muscle1_1.vti','muscle1_2.vti','muscle1_3.vti','muscle1_4.vti','muscle1_5.vti','muscle1_6.vti','muscle1_7.vti']
muscle_list2    = ['muscle2_1.vti','muscle2_2.vti','muscle2_3.vti','muscle2_4.vti','muscle2_5.vti','muscle2_6.vti','muscle2_7.vti']
ligament1_list  = ['ligament1_1.vti','ligament1_2.vti','ligament1_3.vti','ligament1_4.vti','ligament1_5.vti','ligament1_6.vti','ligament1_7.vti']
ligament2_list  = ['ligament2_1.vti','ligament2_2.vti','ligament2_3.vti','ligament2_4.vti','ligament2_5.vti','ligament2_6.vti','ligament2_7.vti']
tendon1_list    = ['tendon1_1.vti','tendon1_2.vti','tendon1_3.vti','tendon1_4.vti','tendon1_5.vti','tendon1_6.vti','tendon1_7.vti']
tendon2_list    = ['tendon2_1.vti','tendon2_2.vti','tendon2_3.vti','tendon2_4.vti','tendon2_5.vti','tendon2_6.vti','tendon2_7.vti']
menis_list      = ['kneecap_1.vti','kneecap_2.vti','kneecap_3.vti','kneecap_4.vti','kneecap_5.vti','kneecap_6.vti','kneecap_7.vti']


#Define the colors for the anatomic structures in RGBA 
colors = vtk.vtkNamedColors()
colors.SetColor("SkinColor", [177,122,101, 255])
colors.SetColor('boneColor', [241,214,145,255])
colors.SetColor('muscleColor', [192,104,88,255])
colors.SetColor('ligamentColor',[153,255,204,255] )
colors.SetColor('MeniscusColor', [255,255,153, 255])
colors.SetColor('tendonColor', [153,153,255,255])

#Define the colors for the anatomic structures in normalized RGB
skinColor = [float(177)/255,float(122)/255,float(101)/255]
boneColor = [float(241)/255,float(214)/255,float(145)/255]
muscleColor = [float(192)/255,float(104)/255,float(88)/255]
ligamentColor = [float(153)/255,float(255)/255,float(204)/255]
meniscusColor = [float(255)/255,float(255)/255,float(153)/255]
tendonColor = [float(153)/255,float(153)/255,float(204)/255]

#Define the renderer and background
ren = vtk.vtkRenderer()
ren.SetBackground(0.2,0.2,0.2)

#Define the renderwindow and size
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
renWin.SetSize(1000, 1500)

#Define the interactor
iren = vtk.vtkRenderWindowInteractor()
iren.SetInteractorStyle(MyInteractorStyle())
iren.SetRenderWindow(renWin)

#Define the VTI files data readers
skin = vtk.vtkXMLImageDataReader()
bones = vtk.vtkXMLImageDataReader()
muscle1 = vtk.vtkXMLImageDataReader()
muscle2 = vtk.vtkXMLImageDataReader()
tendon1 = vtk.vtkXMLImageDataReader()
tendon2 = vtk.vtkXMLImageDataReader()
ligament1 = vtk.vtkXMLImageDataReader()
ligament2 = vtk.vtkXMLImageDataReader()
menis = vtk.vtkXMLImageDataReader()

#Set per data reader the appropriate path to the file
skin.SetFileName("Structures/"+skin_list[0])
bones.SetFileName("Structures/"+bone_list[0])
muscle1.SetFileName("Structures/"+muscle_list1[0])
muscle2.SetFileName("Structures/"+muscle_list2[0])
tendon1.SetFileName("Structures/"+tendon1_list[0])
tendon2.SetFileName("Structures/"+tendon2_list[0])
ligament1.SetFileName("Structures/"+ligament1_list[0])
ligament2.SetFileName("Structures/"+ligament2_list[0])
menis.SetFileName("Structures/"+menis_list[0])


### VOLUME RENDER ###

### Volume Rendering Skin ###
#The scalar values
scalarSkin  = [50,51,1100,1101]
#The different color values
colorSkin   = [[0.0, 0.0, 0.0],skinColor,skinColor,[0.0,0.0,0.0]]
#The opacity's per scalar
opacSkin    = [0.00,0.03,0.03,0.00]
#The piecewise function for opacity within the structures
pieceSkin   = [0.1,0.9,1.0]
volumeSkin  = createVolumeRender(skin,scalarSkin,colorSkin,opacSkin,pieceSkin)

### Volume Rendering Bone ###
scalarBone  = [50,51,1100,1101]
colorBone   = [[0.0, 0.0, 0.0],boneColor,boneColor,[0.0,0.0,0.0]]
opacBone    = [0.00,1.00,1.00,0.00]
pieceBone   = [0.1,0.9,1.0]
volumeBone  = createVolumeRender(bones,scalarBone,colorBone,opacBone,pieceBone)

### Volume Rendering Muscle ###
scalarMuscle     = [50,51,1100,1101]
colorMuscle      = [[0.0, 0.0, 0.0],muscleColor,muscleColor,[0.0,0.0,0.0]]
opacMuscle       = [0.00,1.0,1.0,0.00]
pieceMuscle      = [0.1,0.9,1.0]
volumeMuscle1    = createVolumeRender(muscle1,scalarMuscle,colorMuscle,opacMuscle,pieceMuscle)
volumeMuscle2    = createVolumeRender(muscle2,scalarMuscle,colorMuscle,opacMuscle,pieceMuscle)

### Volume rendering for Ligament ###
scalarLigament     = [50,51,1100,1101]
colorLigament      = [[0.0, 0.0, 0.0],ligamentColor,ligamentColor,[0.0,0.0,0.0]]
opacLigament       = [0.00,0.5,0.5,0.00]
pieceLigament      = [0.1,0.9,1.0]
volumeLigament1    = createVolumeRender(ligament1,scalarLigament,colorLigament,opacLigament,pieceLigament)
volumeLigament2    = createVolumeRender(ligament2,scalarLigament,colorLigament,opacLigament,pieceLigament)

### Volume rendering for Tendon ###
scalarTendon    = [50,51,1100,1101]
colorTendon     = [[0.0, 0.0, 0.0],tendonColor,tendonColor,[0.0,0.0,0.0]]
opacTendon      = [0.00,0.5,0.5,0.00]
pieceTendon     = [0.1,0.9,1.0]
volumeTendon1    = createVolumeRender(tendon1,scalarTendon,colorTendon,opacTendon,pieceTendon)
volumeTendon2   = createVolumeRender(tendon2,scalarTendon,colorTendon,opacTendon,pieceTendon)

### Volume Rendering for Meniscus ###
scalarMenis     = [50,51,1100,1101]
colorMenis      = [[0.0, 0.0, 0.0],meniscusColor,meniscusColor,[0.0,0.0,0.0]]
opacMenis       = [0.00,0.5,0.5,0.00]
pieceMenis      = [0.1,0.9,1.0]
volumeMenis     = createVolumeRender(menis,scalarMenis,colorMenis,opacMenis,pieceMenis)


### ISOSURFACE RENDER ###

# make the skin actor
skinActor = createKneeSkin(skin, 10, 20)
skinActor.GetProperty().SetColor(colors.GetColor3d("SkinColor"))
skinActor.GetProperty().SetOpacity(1)

# make the bone actor:
boneActor  = createKneeSkin(bones, 10, 10)
boneActor.GetProperty().SetColor(colors.GetColor3d("white"))
boneActor.GetProperty().SetOpacity(1)

# make the muscle actor1:
muscleActor1  = createKneeSkin(muscle1, 10, 15 )
muscleActor1.GetProperty().SetColor(colors.GetColor3d("muscleColor"))
muscleActor1.GetProperty().SetOpacity(1)

# make the muscle actor2:
muscleActor2  = createKneeSkin(muscle2, 10, 15 )
muscleActor2.GetProperty().SetColor(colors.GetColor3d("muscleColor"))
muscleActor2.GetProperty().SetOpacity(1)

# make the ligament actors
ligament1Actor = createKneeSkin(ligament1, 5, 5)
ligament1Actor.GetProperty().SetColor(colors.GetColor3d("ligamentColor"))
ligament1Actor.GetProperty().SetOpacity(1)

# make the ligament actor:
ligament2Actor  = createKneeSkin(ligament2, 5, 5)
ligament2Actor.GetProperty().SetColor(colors.GetColor3d("ligamentColor"))
ligament2Actor.GetProperty().SetOpacity(1)

# make the tendon actor:
tendon1Actor  = createKneeSkin(tendon1, 10, 5)
tendon1Actor.GetProperty().SetColor(colors.GetColor3d("tendonColor"))
tendon1Actor.GetProperty().SetOpacity(1)

### make the tendon actor2 with isosurface ###
tendon2Actor = createKneeSkin(tendon2, 10, 5 )
tendon2Actor.GetProperty().SetColor(colors.GetColor3d("tendonColor"))
tendon2Actor.GetProperty().SetOpacity(1)

# make the menis actor:
menisActor  = createKneeSkin(menis, 10, 10)
menisActor.GetProperty().SetColor(colors.GetColor3d("MeniscusColor"))
menisActor.GetProperty().SetOpacity(1)


### ACTORS

# Add the actors to the renderer
ren.AddActor(ligament1Actor)
ren.AddActor(ligament2Actor)
ren.AddActor(boneActor)
ren.AddActor(muscleActor1)
ren.AddActor(muscleActor2)
ren.AddActor(tendon2Actor)
ren.AddActor(tendon1Actor)
ren.AddActor(menisActor)
ren.AddActor(skinActor)


### SlIDERS ###

### Slider for flexion of the knee ###
StyleDim = [0.008,0.008,0.03,0.00]
StyleN1 = createSliderStyle(0,7,0,[0.05,0.1],[0.95,0.1], "Knee flexion", StyleDim)

sliderWidgetN1 = vtk.vtkSliderWidget()
sliderWidgetN1.SetInteractor(iren)
sliderWidgetN1.SetRepresentation(StyleN1)
sliderWidgetN1.SetAnimationModeToAnimate()
sliderWidgetN1.EnabledOn()
sliderWidgetN1.AddObserver(vtk.vtkCommand.InteractionEvent, SliderFlexion(skin, bones, muscle1, muscle2, ligament1, ligament2, tendon1, tendon2, menis))

### Render Style Slider ###
StyleDim = [0.008,0.008,0.015,0.015]
styleStyle = createSliderStyle(0,1,0,[0.05,0.9],[0.25,0.9], "Render Style", StyleDim)

SliderStyleWidget = vtk.vtkSliderWidget()
SliderStyleWidget.SetInteractor(iren)
SliderStyleWidget.SetRepresentation(styleStyle)
SliderStyleWidget.SetAnimationModeToAnimate()
SliderStyleWidget.EnabledOn()
SliderStyleWidget.AddObserver(vtk.vtkCommand.InteractionEvent, ChangeRenderStyle(muscle1))

### Skin Opacity Slider ###
StyleDim = [0.008,0.008,0.015,0.015]
StyleSkin = createSliderStyle(0,100,100,[0.75,0.9],[0.95,0.9], "Skin opacity", StyleDim)

sliderSkinWidget = vtk.vtkSliderWidget()
sliderSkinWidget.SetInteractor(iren)
sliderSkinWidget.SetRepresentation(StyleSkin)
sliderSkinWidget.SetAnimationModeToAnimate()
sliderSkinWidget.EnabledOn()

sliderSkinWidget.AddObserver(vtk.vtkCommand.InteractionEvent, SliderOpacity(scalarSkin))

### Bone Opacity Slider ###
StyleDim = [0.008,0.008,0.015,0.015]
styleBone = createSliderStyle(0,100,100,[0.75,0.8],[0.95,0.8], "Bone opacity", StyleDim)

sliderBoneWidget = vtk.vtkSliderWidget()
sliderBoneWidget.SetInteractor(iren)
sliderBoneWidget.SetRepresentation(styleBone)
sliderBoneWidget.SetAnimationModeToAnimate()
sliderBoneWidget.EnabledOn()

sliderBoneWidget.AddObserver(vtk.vtkCommand.InteractionEvent, BoneOpacity(scalarBone))

### Muscle Opacity Slider ###
StyleDim = [0.008,0.008,0.015,0.015]
styleMuscle = createSliderStyle(0,100,100,[0.75,0.7],[0.95,0.7], "Muscle opacity", StyleDim)

sliderMuscleWidget = vtk.vtkSliderWidget()
sliderMuscleWidget.SetInteractor(iren)
sliderMuscleWidget.SetRepresentation(styleMuscle)
sliderMuscleWidget.SetAnimationModeToAnimate()
sliderMuscleWidget.EnabledOn()

sliderMuscleWidget.AddObserver(vtk.vtkCommand.InteractionEvent, MuscleOpacity(scalarMuscle))

### Tendon Opacity Slider ###
StyleDim = [0.008,0.008,0.015,0.015]
styleTendon = createSliderStyle(0,100,100,[0.75,0.6],[0.95,0.6], "Tendon opacity", StyleDim)

sliderTendonWidget = vtk.vtkSliderWidget()
sliderTendonWidget.SetInteractor(iren)
sliderTendonWidget.SetRepresentation(styleTendon)
sliderTendonWidget.SetAnimationModeToAnimate()
sliderTendonWidget.EnabledOn()

sliderTendonWidget.AddObserver(vtk.vtkCommand.InteractionEvent, TendonOpacity(scalarTendon))

### Ligament Opacity Slider ###
StyleDim = [0.008,0.008,0.015,0.015]
styleLigament = createSliderStyle(0,100,100,[0.75,0.5],[0.95,0.5], "Ligament opacity", StyleDim)

sliderLigamentWidget = vtk.vtkSliderWidget()
sliderLigamentWidget.SetInteractor(iren)
sliderLigamentWidget.SetRepresentation(styleLigament)
sliderLigamentWidget.SetAnimationModeToAnimate()
sliderLigamentWidget.EnabledOn()

sliderLigamentWidget.AddObserver(vtk.vtkCommand.InteractionEvent, LigamentOpacity(scalarLigament))

### Meniscus Opacity Slider ###
StyleDim = [0.008,0.008,0.015,0.015]
styleMeniscus = createSliderStyle(0,100,100,[0.75,0.4],[0.95,0.4], "Meniscus opacity", StyleDim)

sliderMeniscusWidget = vtk.vtkSliderWidget()
sliderMeniscusWidget.SetInteractor(iren)
sliderMeniscusWidget.SetRepresentation(styleMeniscus)
sliderMeniscusWidget.SetAnimationModeToAnimate()
sliderMeniscusWidget.EnabledOn()

sliderMeniscusWidget.AddObserver(vtk.vtkCommand.InteractionEvent, MeniscusOpacity(scalarMenis))


### Setup initial camera positon ###
camera =  ren.GetActiveCamera()
c = volumeSkin.GetCenter()
camera.SetFocalPoint(c[0], c[1], c[2])
camera.SetPosition(315, 192, 1019)
camera.SetViewUp(0.98, 0.094, -0.122)


### Text widget ###

# Create the TextActor
text_actor = vtk.vtkTextActor()
text_actor.SetInput("Press spacebar for live animation!")
text_actor.GetTextProperty().SetColor((1, 1, 1))

# Create the text representation. Used for positioning the text_actor
text_representation = vtk.vtkTextRepresentation()
text_representation.GetPositionCoordinate().SetValue(0.30, 0.15)
text_representation.GetPosition2Coordinate().SetValue(0.5, 0.1)

# Text widget
text_widget = vtk.vtkTextWidget()
text_widget.SetRepresentation(text_representation)
text_widget.SetInteractor(iren)
text_widget.SetTextActor(text_actor)
text_widget.SelectableOff()
text_widget.On()

### Render and start ###
renWin.Render()
iren.Initialize()
iren.Start()


print ("Cleanup time")
# Free up any objects we created (useless really, as we quit anyway)
contour = None
mapper = None
actor = None
ren1 = None
renWin = None


















