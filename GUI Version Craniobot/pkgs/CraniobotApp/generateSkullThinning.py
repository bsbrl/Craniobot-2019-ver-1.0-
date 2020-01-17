"""
Craniobot: generate skull thinning gcode commands
University of Minnesota - Twin Cities
Biosensing and Biorobotics Lab
author: Daniel Sousa Schulman
email: sousa013@umn.edu // dschul@umich.edu
PI: Suhasa Kodandaramaiah (suhasabk@umn.edu)
"""
import numpy as np
import json
from math import *
import matplotlib.pyplot as plt


class GenerateSkullThinning():
    def __init__(self, x1,y1,x2,y2,max_step):
        #points to define the two opposite corners of a rectangle
        self.writeProbeGCode(x1,y1,x2,y2,max_step)
        
    def writeProbeGCode(self, x1,y1,x2,y2,max_step):
        #gap between points = 0.15mm
        col=int(abs(x2-x1)/0.15)+1
        row=int(abs(y2-y1)/0.15)+1
        logo_coordinates=[[0]*(col*row) for i in range(2)] #first element for x, second y
        counter=0
        multiplier=1
        directionX=1
        directionY=1
        if(x2<x1):
            directionX=-1
        if(y2<y1):
            directionY=-1
        for i in range(col):
            for j in range(row):
                logo_coordinates[0][counter]=x1+directionX*i*0.15
                if(multiplier>0): #increasing in y
                    logo_coordinates[1][counter]=y1+directionY*j*0.15
                else: #decreasing in y
                    logo_coordinates[1][counter]=y1+directionY*(row-j-1)*0.15
                counter=counter+1
            multiplier=multiplier*-1 #create snake like pattern

        
        #Check step size between points and compare to max_step
        num_steps = len(logo_coordinates[0])-1
        n=0
        for x in range(num_steps):
            #Caculate distance between two steps. Do we need to interpolate?
            #DEBUG print("n={}".format(n))
            a = logo_coordinates[0][n+1]-logo_coordinates[0][n]
            #DEBUG print("a={}".format(a))
            b = logo_coordinates[1][n+1]-logo_coordinates[1][n]
            #DEBUG print("b={}".format(b))
            L = sqrt(a*a+b*b)
            #DEBUG print("L={}".format(L))
            if L > max_step:
                num_interp = int(ceil(L/max_step))
                #DEBUG print(num_interp)
                x_inc = a/num_interp
                y_inc = b/num_interp
                for m in range(num_interp-1):
                    #DEBUG print("m={}".format(m))
                    x_start = logo_coordinates[0][n]
                    y_start = logo_coordinates[1][n]
                    logo_coordinates[0].insert(n+m+1, x_start + (m+1)*x_inc)
                    logo_coordinates[1].insert(n+m+1, y_start + (m+1)*y_inc)
                n = n+num_interp
                    
            else:
                #DEBUG print("step is OK")
                n=n+1
        
        
        
        logo_coordinates[0] = [round(x,4) for x in logo_coordinates[0]]
        logo_coordinates[1] = [round(x,4) for x in logo_coordinates[1]]

        plt.plot(logo_coordinates[0],logo_coordinates[1],'r.')
        plt.plot(logo_coordinates[0],logo_coordinates[1],'k-')
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()
        
                
        self.gCode = list()
        
        #First, set the current position (bregma) as the origin
        gc_line = {"gc":"g28.3x0y0z0"}
        number_pts = len(logo_coordinates[0])
        self.gCode.append(gc_line)
        for num in range(0,number_pts):
            #Now, raise up z 0.5mm for clearance. Traverse to new (x,y) and run g38.2 probe command. Reapeat for each (x,y).
            gc_line = {"gc":"g91g1f100z0.5"}
            self.gCode.append(gc_line)
            
            gc_line = {"gc":"g90g1f100x{:.4f}y{:.4f}" .format(logo_coordinates[0][num],logo_coordinates[1][num])}
            self.gCode.append(gc_line)
            
            gc_line = {"gc":"g38.2f5z-10"}
            self.gCode.append(gc_line)
        
        #End by going back to 1mm 
        gc_line = {"gc":"g90g1f100z1"}
        self.gCode.append(gc_line)
        
        gc_line = {"gc":"g90g1f100x0y0"}
        self.gCode.append(gc_line)
        
        #Now add a end of program m2 flag
        gc_line = {"gc":"m2"}
        self.gCode.append(gc_line)

       