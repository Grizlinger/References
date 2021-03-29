# -*- coding: utf-8 -*-
"""CellNN_course_04_work.ipynb másolata

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1wOr2938YI8LhI3RVe0Fc-Xg9Oo8Ubhkm
"""

#download the simulator
!wget https://users.itk.ppke.hu/~horan/cnn/CellSim.py
#download the labirinth image and initial points
!wget https://users.itk.ppke.hu/~horan/cnn/Lab.npy
!wget https://users.itk.ppke.hu/~horan/cnn/LabInit.npy

# Commented out IPython magic to ensure Python compatibility.
#importing the standard Python modules
import numpy as np
import cv2
import matplotlib.pyplot as plt
import CellSim                    
# %matplotlib inline

Lab=np.load('Lab.npy')
plt.imshow(Lab, cmap='Greys')
Init=np.load('LabInit.npy')
plt.figure()
plt.imshow(Init, cmap='Greys')

#Iterative solution
CNN=CellSim.CellSim() #intialization of the simulator


CNN.SetTimeStep(0.1) #setting the timestep of the numerical solution
CNN.SetSimTime(1.0) #setting the running time of the simulation

CNN.Input=Lab #loading the input image
CNN.State=np.zeros_like(Lab) #loading the initial state
CNN.Boundary='ZeroFlux'  #setting the  Boundary condition

for i in range(25):
  # endeater template
  CNN.SetA([[0.0,0.0,0.0], [0.0,0.0,0.0], [0.0,0.0,0.0]])
  CNN.SetB([[0.0,1.0,0.0], [1.0,9.0,1.0], [0.0,1.0,0.0]])
  CNN.SetZ(8.0)
  OutImg = CNN.Simulate()

  # LOGAND template
  CNN.Input=Init #loading the input image
  CNN.State=OutImg #loading the initial state  
  CNN.SetA([[0.0,0.0,0.0], [0.0,2.0,0.0], [0.0,0.0,0.0]])
  CNN.SetB([[0.0,0.0,0.0], [0.0,1.0,0.0], [0.0,0.0,0.0]])
  CNN.SetZ(-1.0)
  OutImg = CNN.Simulate()

  CNN.Input=OutImg #loading the input image
  CNN.State=np.zeros_like(Lab) #loading the initial state


plt.imshow(Lab, cmap='Greys')
plt.figure()
plt.imshow(OutImg, cmap='Greys') #displaying the output image

#Continuous solution
CNN=CellSim.CellSim() #intialization of the simulator

CNN.SetTimeStep(0.1) #setting the timestep of the numerical solution
CNN.SetSimTime(5.0) #setting the running time of the simulation

CNN.Input=Init #loading the input image
CNN.State=Lab #loading the initial state
CNN.Boundary='ZeroFlux'  #setting the  Boundary condition


# pathfinder template
CNN.SetA([[0.0,1.0,0.0], [1.0,9.0,1.0], [0.0,1.0,0.0]])
CNN.SetB([[0.0,0.0,0.0], [0.0,8.0,0.0], [0.0,0.0,0.0]])
CNN.SetZ(8.0)
OutImg = CNN.Simulate()

OutImg=CNN.Simulate() #executing the simulation, the function returns the output image of the CeNN array
plt.imshow(Lab, cmap='Greys') #displaying the input image
plt.figure()
plt.imshow(OutImg, cmap='Greys') #displaying the output image