#!/usr/bin/env python

import cv2
import timeit
import numpy as np

from dot import *
from video import *

# Lines should be lists of dots strictly of size 2
# Boxes should be quadruples of lines starting from roof and continuing clock-wise.
# Have to take care of the fact that the line finalized is not already drawn. Done now.
# Have to incorporate the handling of successive frames. Done now.
# Player to draw the next line should be kept track of. Very IMP. Done now.
# What about the co-ordinates of the dots? Convert to standard unitless Cartesian co-ordinates.

# Line functions

# Tanmoy's progress bar grid

class Grid(object):
      def __init__(self,row=4,col=4,dotRadius=4,dotsGap=20,dottype=0,color=(255,0,0)):   #dotsGap includes dotRadius
          self.row=row
          self.col=col
          self.dotRadius=dotRadius
          self.dotsGap=dotsGap
          self.dottype=dottype
          self.color=color
          self.height=(row-1)*dotsGap+2*dotRadius
          self.width=(col-1)*dotsGap+2*dotRadius
          self.grid=np.zeros((self.width,self.height,3),np.uint8)
          self.dotPosList=[]
          self.linecolor=(0,210,11)
          self.currenLineColor=(112,21,221)
          self.player1boxcolor=(255,128,12)
          self.player2boxcolor=(0,128,12)
          self.lastDrawnLinePos=None 
          self.lastSelectedLine=[(0,0),(0,1)]                   
          self.progress_bar_drawn_over_line=None 
          self.filldots()
          
          
          
      #called internally    
      def filldots(self):
          y=self.dotRadius
          i=0
          while y<self.width:
            x=self.dotRadius
            self.dotPosList.append([])
            while x<self.height:
              self.createDotAt(x,y)
              self.dotPosList[i].append((x,y))
              x+=self.dotsGap
            y+=self.dotsGap
            i+=1
     
     
      #called internally
      def createDotAt(self,x,y):
          if self.dottype==0:
             cv2.circle(self.grid,(x,y), self.dotRadius, self.color, -1)
          else:
             cv2.rectangle(self.grid,(x-self.dotRadius,y-self.dotRadius),(x+self.dotRadius,y+self.dotRadius), self.color, -1) 
     
     
      #called internally
      def displayGrid(self):
          cv2.imshow("grid window",self.grid)
      
      
      #called internally   
      def detectHorizontalLine(self,x,y):
             linePossibility=False
             for i in xrange (self.row):
               if y>self.dotPosList[i][0][1]-self.dotRadius and y<self.dotPosList[i][0][1]+self.dotRadius:
                  linePossibility=True
                  break;
             if linePossibility==True:              
               for j in xrange (self.col-1):
                     if x>self.dotPosList[0][j][0]+self.dotRadius and x<self.dotPosList[0][j+1][0]-self.dotRadius:
                        return (i,j)
             return None
      
      #called internally
      def detectVerticalLine(self,x,y):
             linePossibility=False
             for j in xrange(self.col):
               if x>self.dotPosList[0][j][0]-self.dotRadius and x<self.dotPosList[0][j][0]+self.dotRadius:
                  linePossibility=True
                  break;
             if linePossibility==True:
                for i in xrange (self.row-1):
                      if y>self.dotPosList[i][0][1]+self.dotRadius and y<self.dotPosList[i+1][0][1]-self.dotRadius:
                         return (i,j)
             return None
      
      #called internally
      def isOutsideArea(self,x,y):
           if y<=self.dotPosList[0][0][1]-self.dotRadius or y>=self.dotPosList[self.row-1][0][1]+self.dotRadius \
           or x<=self.dotPosList[0][0][0]-self.dotRadius or x>=self.dotPosList[0][self.col-1][0]+self.dotRadius:
             return True
           else:
             return False
             
      #this is called to detect if line is selected      
      def findSelectedLine(self,location,location_y_if_first_arg_is_x=None):
           if location_y_if_first_arg_is_x==None:
              x,y=location[0],location[1]
           else:
              x,y=location,location_y_if_first_arg_is_x
           if self.isOutsideArea(x,y):
              return None
              
           startingDotOfLine=self.detectHorizontalLine(x,y)
           if startingDotOfLine!=None:
              self.lastSelectedLine=[startingDotOfLine,(startingDotOfLine[0],startingDotOfLine[1]+1)]
              return list(self.lastSelectedLine)
              
           startingDotOfLine=self.detectVerticalLine(x,y)
           if startingDotOfLine!=None:
              self.lastSelectedLine=[startingDotOfLine,(startingDotOfLine[0]+1,startingDotOfLine[1])]
              return list(self.lastSelectedLine)
           return None
           
           
      #called internally     
      def drawHorizontalLine(self,line,color):  
          startingDotPos=self.dotPosList[line[0][0]][line[0][1]]
          endingDotPos=self.dotPosList[line[1][1]][line[1][1]]
          lineTopLeftPos=(startingDotPos[0]+self.dotRadius+1,startingDotPos[1]-self.dotRadius)
          lineBottomRightPos=(endingDotPos[0]-self.dotRadius-1,endingDotPos[1]+self.dotRadius)
          cv2.rectangle(self.grid, lineTopLeftPos, lineBottomRightPos, color, -1)
          return (lineTopLeftPos,lineBottomRightPos)

      #called internally
      def drawVerticalLine(self,line,color):   
          startingDotPos=self.dotPosList[line[0][0]][line[0][1]]
          endingDotPos=self.dotPosList[line[1][0]][line[1][1]]
          lineTopLeftPos=(startingDotPos[0]-self.dotRadius,startingDotPos[1]+self.dotRadius+1)
          lineBottomRightPos=(endingDotPos[0]+self.dotRadius,endingDotPos[1]-self.dotRadius-1)
          cv2.rectangle(self.grid, lineTopLeftPos, lineBottomRightPos, color, -1)
          return (lineTopLeftPos,lineBottomRightPos)

           
      #draws a line, this function is called internally    
      def drawLine(self,line):
          if self.lastDrawnLinePos!=None:
             cv2.rectangle(self.grid, self.lastDrawnLinePos[0], self.lastDrawnLinePos[1], self.linecolor, -1)
          if line[0][0]==line[1][0]:
             self.lastDrawnLinePos=self.drawHorizontalLine(line,self.currenLineColor)
          else:
             self.lastDrawnLinePos=self.drawVerticalLine(line,self.currenLineColor)
          
          
      #this will be called for drawing the last selected line         
      def drawLastSelectedLine(self):
           self.drawLine(self.lastSelectedLine)
           
      #this is called to draw a box     
      def drawBox(self,dotCoord,boxcolor=0):
          if boxcolor==0:
              boxcolor=self.player1boxcolor
          else:
              boxcolor=self.player2boxcolor
          startingDotPos=self.dotPosList[dotCoord[0]][dotCoord[1]]
          endingDotPos=self.dotPosList[dotCoord[0]+1][dotCoord[1]+1]
          boxStartPoint=(startingDotPos[0]+self.dotRadius+1,startingDotPos[1]+self.dotRadius+1)
          boxEndPoint=(endingDotPos[0]-self.dotRadius-1,endingDotPos[1]-self.dotRadius-1)
          cv2.rectangle(self.grid,boxStartPoint,boxEndPoint, boxcolor, -1)
          
      def calculateBarLength(self,i):
          barLength=int(round((self.dotsGap-2*self.dotRadius)*i))
          if barLength<0:
            barLength=0
          elif barLength>self.dotsGap-2*self.dotRadius-2:
            barLength=self.dotsGap-2*self.dotRadius-2
          return barLength
          
      #called internally
      def drawHorizontalProgressLine(self,line,color,i):
          startingDotPos=self.dotPosList[line[0][0]][line[0][1]]
          barLength=self.calculateBarLength(i)
          lineTopLeftPos=(startingDotPos[0]+self.dotRadius+1,startingDotPos[1]-self.dotRadius)
          lineBottomRightPos=(lineTopLeftPos[0]+barLength,lineTopLeftPos[1]+2*self.dotRadius)
          cv2.rectangle(self.grid, lineTopLeftPos, lineBottomRightPos, self.currenLineColor, -1)
     
      #called internally
      def drawVerticalProgressLine(self,line,color,i):
          startingDotPos=self.dotPosList[line[0][0]][line[0][1]]
          barLength=self.calculateBarLength(i)
          lineTopLeftPos=(startingDotPos[0]-self.dotRadius,startingDotPos[1]+self.dotRadius+1)
          lineBottomRightPos=(lineTopLeftPos[0]+2*self.dotRadius,lineTopLeftPos[1]+barLength)
          cv2.rectangle(self.grid, lineTopLeftPos, lineBottomRightPos, self.currenLineColor, -1)
     
      
      
      def drawProgressBarOverLastSelectedLine(self,i):
                 line=self.lastSelectedLine
                 if line[0][0]==line[1][0]:
                     self.drawHorizontalProgressLine(line,self.currenLineColor,i)
                 else:
                     self.drawVerticalProgressLine(line,self.currenLineColor,i)
                 self.progress_bar_drawn_over_line=line
             

      def removeProgressBar(self):
                  line=self.progress_bar_drawn_over_line
                  if line==None:
                     return
                  if line[0][0]==line[1][0]:
                     self.drawHorizontalLine(line,(0,0,0))
                  else:
                     self.drawVerticalLine(line,(0,0,0))

#-----------------------------------------------------------------------------------------------------------------------------------------------
#class Grid(object):
#    def __init__(self,row=4,col=4,dotRadius=4,dotsGap=20,dottype=0,color=(255,0,0)):
#        self.row=row
#        self.col=col
#        self.dotRadius=dotRadius
#        self.dotsGap=dotsGap
#        self.dottype=dottype
#        self.color=color
#        self.height=(row-1)*dotsGap+2*dotRadius
#        self.width=(col-1)*dotsGap+2*dotRadius
#        self.grid=np.zeros((self.width,self.height,3),np.uint8)
#        self.dotPosList=[]
#        self.filldots()
#        self.linecolor=(0,210,11)
#        self.currenLineColor=(112,21,221)
#        self.player1boxcolor=(255,128,12)
#        self.player2boxcolor=(0,128,12)
#        self.lastDrawnLinePos=None

#    def filldots(self):
#        y=self.dotRadius
#        i=0
#        while y<self.width:
#            x=self.dotRadius
#            self.dotPosList.append([])
#            while x<self.height:
#                if self.dottype==0:
#                    cv2.circle(self.grid,(x,y), self.dotRadius, self.color, -1)
#                else:
#                    cv2.rectangle(self.grid,(x-self.dotRadius,y-self.dotRadius),(x+self.dotRadius,y+self.dotRadius), self.color, -1)
#                self.dotPosList[i].append((x,y))
#                x+=self.dotsGap
#            y+=self.dotsGap
#            i+=1

#    def displayGrid(self):
#        cv2.imshow("grid window",self.grid)

#    def detectHorizontalLine(self,x,y):
#        i=0
#        noPossibleLine=True
#        while i<=self.row-1:
#            if y>self.dotPosList[i][0][1]-self.dotRadius and y<self.dotPosList[i][0][1]+self.dotRadius:
#                noPossibleLine=False
#                break;
#            i+=1
#        if noPossibleLine==True:
#            return None
#        j=0
#        while j<=self.col-2:
#            if x>self.dotPosList[0][j][0]+self.dotRadius and x<self.dotPosList[0][j+1][0]-self.dotRadius:
#                return (i,j)
#            j+=1
#        return None

#    def detectVerticalLine(self,x,y):
#        j=0
#        noPossibleLine=True
#        while j<=self.col-1:
#            if x>self.dotPosList[0][j][0]-self.dotRadius and x<self.dotPosList[0][j][0]+self.dotRadius:
#                noPossibleLine=False
#                break;
#            j+=1
#        if noPossibleLine==True:
#            return None
#        i=0
#        while i<=self.col-2:
#           if y>self.dotPosList[i][0][1]+self.dotRadius and y<self.dotPosList[i+1][0][1]-self.dotRadius:
#               return (i,j)
#           i+=1
#        return None

#    def isOutsideArea(self,x,y):
#        if y<=self.dotPosList[0][0][1]-self.dotRadius or y>=self.dotPosList[self.row-1][0][1]+self.dotRadius \
#                or x<=self.dotPosList[0][0][0]-self.dotRadius or x>=self.dotPosList[0][self.col-1][0]+self.dotRadius:
#            return True
#        else:
#            return False

#    def findSelectedLine(self,pointer_location_inside_grid):
#        x=pointer_location_inside_grid[0]
#        y=pointer_location_inside_grid[1]
#        if self.isOutsideArea(x,y):
#            return None
#        lineStartingdot=self.detectHorizontalLine(x,y)
#        if lineStartingdot!=None:
#            self.lastSelectedLine=[lineStartingdot,(lineStartingdot[0],lineStartingdot[1]+1)]
#            return list(self.lastSelectedLine)
#        lineStartingdot=self.detectVerticalLine(x,y)
#        if lineStartingdot!=None:
#            self.lastSelectedLine=[lineStartingdot,(lineStartingdot[0]+1,lineStartingdot[1])]
#            return list(self.lastSelectedLine)
#        return None

#    def drawHorizontalLine(self,line,color):
#        startingDotPos=self.dotPosList[line[0].get_x()][line[0].get_y()]
#        endingDotPos=self.dotPosList[line[1].get_x()][line[1].get_y()]
#        lineTopLeftPos=(startingDotPos[0]+self.dotRadius+1,startingDotPos[1]-self.dotRadius)
#        lineBottomRightPos=(endingDotPos[0]-self.dotRadius-1,endingDotPos[1]+self.dotRadius)
#        cv2.rectangle(self.grid, lineTopLeftPos, lineBottomRightPos, color, -1)
#        return (lineTopLeftPos,lineBottomRightPos)

#    def drawVerticalLine(self,line,color):
#        startingDotPos=self.dotPosList[line[0].get_x()][line[0].get_y()]
#        endingDotPos=self.dotPosList[line[1].get_x()][line[1].get_y()]
#        lineTopLeftPos=(startingDotPos[0]-self.dotRadius,startingDotPos[1]+self.dotRadius+1)
#        lineBottomRightPos=(endingDotPos[0]+self.dotRadius,endingDotPos[1]-self.dotRadius-1)
#        cv2.rectangle(self.grid, lineTopLeftPos, lineBottomRightPos, color, -1)
#        return (lineTopLeftPos,lineBottomRightPos)

#    def drawLine(self,line):
#        if self.lastDrawnLinePos!=None:
#            cv2.rectangle(self.grid, self.lastDrawnLinePos[0], self.lastDrawnLinePos[1], self.linecolor, -1)
#        if line[0].get_x()==line[1].get_x():
#            self.lastDrawnLinePos=self.drawHorizontalLine(line,self.currenLineColor)
#        else:
#            self.lastDrawnLinePos=self.drawVerticalLine(line,self.currenLineColor)

#    def drawLastSelectedLine(self):
#        self.drawLine(self.lastSelectedLine)

#    def drawBox(self,dotCoord,boxcolor=0):
#        if boxcolor==0:
#            boxcolor=self.player1boxcolor
#        else:
#            boxcolor=self.player2boxcolor
#        startingDotPos=self.dotPosList[dotCoord[0]][dotCoord[1]]
#        endingDotPos=self.dotPosList[dotCoord[0]+1][dotCoord[1]+1]
#        boxStartPoint=(startingDotPos[0]+self.dotRadius+1,startingDotPos[1]+self.dotRadius+1)
#        boxEndPoint=(endingDotPos[0]-self.dotRadius-1,endingDotPos[1]-self.dotRadius-1)
#        cv2.rectangle(self.grid,boxStartPoint,boxEndPoint, boxcolor, -1)
#    
##    def denormalize(self,dot):
##        pass

##    def normalize(self,dot):
##        pass

##    def _grid_does_not_fit_in_frame(self):
##        pass

#    def draw_grid(self,frame):
#        another_frame=self.blendGrid(frame,110,300)
#        return frame

#    def blendGrid(self,img1,x=210,y=360):
#        if img1==None:
#            return
#        img2=self.grid
#        img1=cv2.flip(img1, flipCode=1)
#        rows,cols,channels = img2.shape
#        roi = img1[x:x+rows, y:y+cols]
#        
#        img2gray = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
#        ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)
#        mask_inv = cv2.bitwise_not(mask)

#        # Now black-out the area of logo in ROI
#        img1_bg = cv2.bitwise_and(roi,roi,mask = mask_inv)

#        # Take only region of logo from logo image.
#        img2_fg = cv2.bitwise_and(img2,img2,mask = mask)

#        # Put logo in ROI and modify the main image
#        img2_fg= cv2.add(img1_bg,img2_fg)
#        alpha=0.8
#        dst = cv2.addWeighted(roi,1-alpha,img2_fg,alpha,1)
#        img1[x:x+rows, y:y+cols ] = dst
#        return img1
