"""
Craniobot: generate gcode for hole drilling
University of Minnesota
Biosensing and Biorobotics Lab
author: Daniel Sousa Schulman
email: sousa013@umn.edu // dschul@umich.edu
PI: Suhasa Kodandaramaiah (suhasabk@umn.edu)
"""
import numpy as np
import json
import matplotlib.pyplot as plt

class GenerateHoleDrill():
    def __init__(self,x_center,y_center):
        self.number_pts = 1
        self.coordinates = np.zeros((self.number_pts,2))
        self.probe_commands = list()
        self.coordinates[0,0] = x_center
        self.coordinates[0,1] = y_center
        plt.axis([-8,8,-8,8])
        plt.plot(self.coordinates[:,0],self.coordinates[:,1])
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()
        self.writeGCode()
            
    def writeGCode(self):
        #Now write the gcode probe routine to an output file
        self.gCode = list()
        
        #First, set the current position (bregma) as the origin
        gc_line = {"gc":"g28.3x0y0z0"}
        self.gCode.append(gc_line)
        for n in range(0,self.number_pts):
            #Now, raise up z 0.5mm for clearance. Traverse to new (x,y) and run g38.2 probe command. Reapeat for each (x,y).
            gc_line = {"gc":"g91g1f100z0.5"}
            self.gCode.append(gc_line)
            
            gc_line = {"gc":"g90g1f100x{:.4f}y{:.4f}" .format(self.coordinates[n,0],self.coordinates[n,1])}
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
        