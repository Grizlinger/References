# -*- coding: utf-8 -*-
"""CellNN_course_03b.ipynb másolata

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16feU1FZ7TM1nDYoxzmR1z51GgK4VLhUi
"""

# Commented out IPython magic to ensure Python compatibility.
#importing the standard Python modules
import numpy as np
import cv2
import matplotlib.pyplot as plt
import scipy.integrate as numsolver
# %matplotlib inline

def Osc(t,X):
  dots = np.zeros(2)
  dots[0] = X[1]
  dots[1] = -X[0]
  return dots

InitVal = [5,3]
TimeRun = 10
TimeStep = 0.01
States = np.zeros((int(TimeRun/TimeStep)+1, 2))
r = numsolver.ode(Osc).set_integrator('vode', method='bdf', with_jacobian=False)
r.set_initial_value(InitVal, 0)
ind = 0
while r.successful and r.t <= TimeRun:
  r.integrate(r.t+TimeStep)
  States[ind, :] = r.y
  ind+=1

plt.plot(States[:,0], 'b')
plt.plot(States[:,1], 'r')
plt.show

InitVal = [5,3]
TimeRun = 10
TimeStep = 0.01
States = np.zeros((int(TimeRun/TimeStep)+1, 2))

def Euler(f,y0,StartTime,EndTime,h):
  t,y = StartTime,y0
  ind = 0
  while t <= EndTime:
    t+=h
    y+=h*f(t,y)
    States[ind,:]=y
    ind+=1
  return
Euler(Osc,InitVal,0,TimeRun,TimeStep)
plt.plot(States[:,0], 'b')
plt.plot(States[:,1], 'r')
plt.show

#download a test image
!wget https://users.itk.ppke.hu/~horan/avergra2.bmp
!wget https://users.itk.ppke.hu/~horan/cnn/hfimgs/Diffus.bmp

def Uint8ToCell(arr):
  #this function converts an array from unit8, 0-255, oBlack, 255White to -1White, 1Black
  arr = -1*(arr.astype(np.float)/127.5-1.0)
  return arr

def CellToUint8(arr):
  #this function converts an array from -1White, 1Black unit8 to 0-255, oBlack, 255White 
  arr = ((-1*arr)+1)*127.5
  arr = arr.astype(np.uint8)
  return arr

def StandardCNNNonliearity(x):
  #this function implements the standard CNN nonlinearity, all values are saturated below -1 and above 1
  back = x
  back[x<-1] = -1
  back[x>1] = 1
  return back

class CellSim():
  def __init__(self):
      self.Input = []
      self.State = []
      self.Output = []
      self.A = np.zeros((3,3))
      self.B = np.zeros((3,3))
      self.Z = 0
      self.SimTime = 1
      self.TimeStep = 0.1
      self.OutputNonlin = StandardCNNNonliearity
      self.Boundary = 'Constant'
      self.BoundValue = 0

  def GetOutput(self):
      return self.Output

  def SetTimeStep(self,Ts):
      #this function sets the A template of the simulator    
      #check if it is an N times N matrix - later on these could be functions
      self.TimeStep = Ts

  def SetSimTime(self,T):
      #this function sets the A template of the simulator    
      #check if it is an N times N matrix - later on these could be functions
      self.SimTime = T

  def SetInput(self,In):
      #this function sets the A template of the simulator    
      #check if it is an N times N matrix - later on these could be functions
      #and convert image to CellNN domain       
      img=Uint8ToCell(cv2.cvtColor(cv2.imread(In), cv2.COLOR_BGR2GRAY) )
      self.Input = img

  def SetState(self,St):
      #this function sets the A template of the simulator    
      #check if it is an N times N matrix - later on these could be functions
      img=Uint8ToCell(cv2.cvtColor(cv2.imread(St), cv2.COLOR_BGR2GRAY) )
      self.State = img

  def SetZ(self,z):
      self.SetBias(z)

  def SetBias(self,z):
      self.Z=z

  def SetA(self,a):
      self.SetATemplate(a)

  def SetATemplate(self,a):
      #this function sets the A template of the simulator    
      #check if it is an N times N matrix - later on these could be functions
      self.A = a

  def SetB(self,b):
      self.SetBTemplate(b)

  def SetBTemplate(self,b):
      #this function sets the A template of the simulator    
      #check if it is an N times N matrix - later on these could be functions
      self.B = b
  
  def Euler(self,f,y0,StartTime,EndTime,h):
    t,y = StartTime,y0
    while t <= EndTime:
        t += h
        y += h * f(t,y)
    return y
  
  def Simulate(self):
    Ret=self.Euler(self.cell_equation,self.State.flatten(),0, self.SimTime,0.1)
    SizeX=self.State.shape[0]
    SizeY=self.State.shape[1]
    OutImg=self.OutputNonlin(np.reshape(Ret,[SizeX,SizeY]))
    return OutImg

  def cell_equation(self,t,X):
    #This function impelment the differential equation determining the standard cnn cell:
    #xdot = -x + Ay + Bu + z
    #the parameters of the CNN array (templates) are stored in P
    #reshape the 1xN input for the size of the image -ode solvers can only deal with vectors but code is more understandable if    we use arrays
    SizeX=self.State.shape[0]
    SizeY=self.State.shape[1]
    x=np.reshape(X,[SizeX,SizeY])
    #we will return the derivative in this array
    dx=np.zeros( (SizeX,SizeY))

    #go through all elements of the array
    
    for a in range(SizeX):
      for b in range(SizeY):
        if a == 0 or b == 0 or a == SizeX-1 or b == SizeY-1:
          inputregion = np.zeros((3,3))
          stateregion = np.zeros((3,3))

          for c in range(-1,2):
            for d in range(-1,2):
              if self.Boundary == 'Constant':
                if a+c < 0 or b+d < 0 or a+c > SizeX or b+d > SizeY:
                  inputregion[c+1,d+1] = self.BoundValue
                  stateregion[c+1,d+1] = self.BoundValue
                else:
                  inputregion[c+1,d+1] = self.Input[a+c,b+d]
                  stateregion[c+1,d+1] = x[a+c,b+d]
              elif self.Boundary == 'Periodic':
                inda = a+c
                indb = b+d
                if a+c < 0:
                  inda = SizeX-1
                elif a+c > SizeX-1:
                  inda = 0
                if b+d < 0:
                  indb = SizeY-1
                elif b+d > SizeY-1:
                  indb = 0
                inputregion[c+1,d+1] = self.Input[inda,indb]
                stateregion[c+1,d+1] = x[inda,indb]
              elif self.Boundary == 'ZeroFlux':
                inda = a+c
                indb = b+d
                if a+c < 0:
                  inda = 0
                elif a+c > SizeX-1:
                  inda = SizeX-1
                if b+d < 0:
                  indb = 0
                elif b+d > SizeY-1:
                  indb = SizeY-1
                inputregion[c+1,d+1] = self.Input[inda,indb]
                stateregion[c+1,d+1] = x[inda,indb]

        else:  
          inputregion = self.Input[a-1:a+2,b-1:b+2]
          stateregion = x[a-1:a+2,b-1:b+2]
    
        outputregion = self.OutputNonlin(stateregion)
        ForwardCoupling = np.sum(np.multiply(self.B, inputregion))
        FeedbackCoupling = np.sum(np.multiply(self.A, outputregion))
        dx[a, b] = -x[a, b] + FeedbackCoupling + ForwardCoupling + self.Z
    #reshape back to Nx1
    dx=np.reshape(dx,[SizeX*SizeY])
      
    return dx

CNN=CellSim() #intialization of the simulator


CNN.SetTimeStep(0.1) #setting the timestep of the numerical solution
CNN.SetSimTime(5.0) #setting the running time of the simulation
CNN.SetA([[0, 0, 0],[0, 1.0, 0],[0, 0, 0]])  #defining the values of the A template
CNN.SetB([[-1.0, -1.0, -1.0],[-1.0, 8, -1.0],[-1.0, -1.0, -1.0]]) #defining the values of the B template
CNN.Z = -1.0 #Bias
CNN.SetInput('avergra2.bmp')  #loading the input image
CNN.SetState('avergra2.bmp')  #loading the initial state
CNN.Boundary='ZeroFlux'  #setting the  Boundary condition

OutImg=CNN.Simulate() #executing the simulation, the function returns the output image of the CeNN array
plt.imshow(CNN.Input) #displaying the input image
plt.figure()
plt.imshow(OutImg) #displaying the output image