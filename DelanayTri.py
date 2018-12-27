##File Name: Delaunay Triangulation Image Processor
##Date: Dec 26 2018
##Thanks to the Algorithm designer at https://www.cnblogs.com/zhiyishou/p/4430017.html
##Thanks to partner Alice Zhu
##Created by Ling Ma

import tkinter as tk
import math
import cv2
import numpy as np
import random
import os
from tkinter.filedialog import askopenfilename,asksaveasfile
import PIL.Image, PIL.ImageTk
#_____________________GUI Class for testing___________________
class CanvasGUI:
    def __init__(self,triangle):
        self.win=tk.Tk()
        self.win.title("221 final project")
        self.win.config(bg="white")
        self.r=3
        #_____setup canvas_________
        self.canvas=tk.Canvas(self.win)
        self.canvas["width"]=800
        self.canvas["height"]=600
        self.canvas.grid()
        #_____Instance variables_____
        self.oDic={}
        self.lineSet=set()
        self.triangle=triangle #e.g.{((30,30),(40,40),(20,90)),(...)}

    def run(self):
        '''draw the pic'''
        for t in self.triangle:
            d1=self.create_dot(t[0][0],t[0][1])
            d2=self.create_dot(t[1][0],t[1][1])
            d3=self.create_dot(t[2][0],t[2][1])
            self.connect_triangle(d1,d2,d3)
        print("done")
        self.win.mainloop()

    def create_dot(self,x, y, **kwargs):
        '''draw a single dot'''
        o=self.canvas.create_oval(x-self.r,y-self.r,x+self.r,y+self.r,**kwargs,fill="black")
        self.oDic[o]=(x,y)
        return o

    def create_line(self,dot1,dot2):
        '''draw a line bt 2 dots'''
        dot1_x = self.oDic[dot1][0]
        dot1_y = self.oDic[dot1][1]
        dot2_x = self.oDic[dot2][0]
        dot2_y = self.oDic[dot2][1]
        return self.canvas.create_line(dot1_x,dot1_y,dot2_x,dot2_y)

    def connect_triangle(self,dot1,dot2,dot3):
        '''connect 3 dots with lines, add line into set so no replicated line will be created'''
        if (dot1,dot2) and (dot2,dot1) not in self.lineSet:
            self.create_line(dot1,dot2)
            self.lineSet.add((dot1,dot2))
        if (dot3, dot2) and (dot2, dot3) not in self.lineSet:
            self.create_line(dot2,dot3)
            self.lineSet.add((dot2,dot3))
        if (dot1, dot3) and (dot3, dot1) not in self.lineSet:
            self.create_line(dot1,dot3)
            self.lineSet.add((dot1,dot3))
        return (dot1,dot2,dot3)

#_________________Delanay algor__________
class Delaunay_Lawson:
    def __init__(self,dots):
        self.dotList=sorted(dots) #dots list
        self.length=len(dots)
        self.triangles=[] #settled (dot1,dot2,dot3)
        self.temp_triangles=[]#unsettled tri
        self.edgeBuffer=[] #tuple(line1,line2,line3)
        self.Oinfo={}

    def cal_circum_circle(self,triangle):
        '''Calc radius, x, y of a given triangle'''
        x1,y1=triangle[0]
        x2,y2=triangle[1]
        x3,y3=triangle[2]
        a = np.sqrt((x1-x2)**2 + (y1-y2)**2)
        b = np.sqrt((x2-x3)**2 + (y2-y3)**2)
        c = np.sqrt((x1-x3)**2 + (y1-y3)**2)
        S = (1 / 2) * a * b *  np.sqrt(1 - ((a ** 2 + b ** 2 - c ** 2) / (2 * a * b)) ** 2)
        r = (a * b * c) / (4 * S)
        a=np.array([[1,-2*x1,-2*y1],[1,-2*x2,-2*y2],[1,-2*x3,-2*y3]])
        b=np.array([[r**2 -(x1**2+y1**2)],[r**2-(x2**2+y2**2)],[r**2-(x3**2+y3**2)]])
        xx=np.linalg.solve(a,b)
        x,y=xx[1],xx[2]
        return x, y, r

    def getDic(self):
        return self.Oinfo

    def rela_dot_circle(self,dot,x,y,r):
        '''decide dot's position in relation to the circle
            1:dot at right outside the circle, add to triangle
            0:somewhere outside, not sure
            -1:dot inside the circle'''
        if x +r< dot[0]:
            return 1
        elif ((x-dot[0])**2+(y-dot[1])**2) <= r**2:
            return -1
        else:
            return 0

    def gety(self, dot):
        return dot[1]


    def superTriangle(self):
        '''find the super triangle'''
        xmin=self.dotList[0][0]
        xmax=self.dotList[self.length-1][0]
        ylist=sorted(self.dotList,key=self.gety)
        ymin=ylist[0][1]
        ymax=ylist[self.length-1][1]

        midx=(xmax+xmin)/2

        top=(midx,2*ymin-ymax)
        d1=(2*xmax-midx+10,ymax+10)
        d2=(2*xmin-midx-10,ymax+10)
        super = tuple(sorted((top,d1,d2)))
        return super

    def connect_buffer_dots(self,dot):
        '''connect edges in the buffer and dots in the previous triangle'''
        newT=set()
        for ((x1,y1),(x2,y2)) in self.edgeBuffer:
            tri = tuple(sorted((dot,(x1,y1),(x2,y2))))
            if x1 == x2:
                left_slope = math.inf
            else:
                left_slope = (y2-y1)/(x2-x1)

            if x2 == dot[0]:
                right_slope = math.inf
            else:
                right_slope = (dot[1]-y2)/(dot[0]-x2)

            if left_slope != right_slope:
                newT.add(tri)
                self.Oinfo[tri] = Delaunay_Lawson.cal_circum_circle(self,tri)

        return list(newT)


    def calculate(self):
        '''Main'''
        super=self.superTriangle()
        self.triangles.append(super)
        self.temp_triangles.append(super)
        self.Oinfo[super]=Delaunay_Lawson.cal_circum_circle(self,super)
        for dot in self.dotList:
            pointer = 0
            self.edgeBuffer.clear()
            while pointer < len(self.temp_triangles):
                Ttri = self.temp_triangles[pointer]
                x,y, radius = self.Oinfo[Ttri]
                result=self.rela_dot_circle(dot,x,y,radius)
                if result==1:
                    self.triangles.append(Ttri)
                    self.temp_triangles.remove(Ttri)
                elif result==0:
                    pointer+=1
                    continue
                else:
                    c1 = tuple(sorted((Ttri[0], Ttri[1])))
                    c2 = tuple(sorted((Ttri[0], Ttri[2])))
                    c3 = tuple(sorted((Ttri[1], Ttri[2])))
                    self.edgeBuffer.append(c1)
                    self.edgeBuffer.append(c2)
                    self.edgeBuffer.append(c3)
                    for c in [c1,c2,c3]:
                        if self.edgeBuffer.count(c)==2:
                            self.edgeBuffer.remove(c)
                            self.edgeBuffer.remove(c)
                    self.temp_triangles.remove(Ttri)
            self.temp_triangles+=self.connect_buffer_dots(dot)
        self.triangles+=self.temp_triangles
        ans=[]
        for (a,b,c) in self.triangles:
            if a not in super and b not in super and c not in super:
                ans.append((a,b,c))
        return ans



#_________________________________random_List for testing_____________
def gene_random_list(n):
    list=set()
    for i in range(n):
        list.add((random.randint(0,700),random.randint(0,460)))
    return list

dots1={(30,30),(100,30),(30,100),(100,100),(200,400)}

dots={(277, 249), (372, 55), (259, 140), (280, 157), (129, 172), (374, 204), (77, 346), (382, 72), (109, 368), (137, 311), (153, 237), (355, 50), (334, 259), (379, 267), (126, 359), (272, 57), (213, 300), (321, 75), (321, 350), (368, 204)}

# dots2=gene_random_list(200)
# print(dots)
# ans=Delaunay_Lawson(dots).calculate()
# gui=CanvasGUI(ans)
# gui.run()
# print(max(ans),"and we have:")

#___________________________Main________________________
img="C:/Users/lma11/Pictures/LingMa MSP/2.jpg"
class Board:
    def __init__(self, window, window_title, image_path=img):
        self.wd=window
        self.wd.title(window_title)

        self.selectedPic=image_path

        self.cv_img = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)

        self.height, self.width, no_channels = self.cv_img.shape
        # ___set up Canvas
        self.canvas = tk.Canvas(window, width=self.width, height=self.height)
        self.canvas.pack()
        # ___process & store image
        self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.cv_img))
        self.canvas.create_image(10, 50, image=self.photo, anchor=tk.NW)
        #____upload button
        self.btn_up=tk.Button(self.wd,text="Upload an Image",width=20,command=self.uploadPic)
        self.btn_up.pack(anchor=tk.CENTER,expand=True)

        self.btn_process=tk.Button(self.wd,text="Triangulate", width=20,command=self.triangulate)
        self.btn_process.pack(anchor=tk.CENTER, expand=True)

        self.btn_save=tk.Button(self.wd,text="Save to local",width=20, command=self.save)
        self.btn_save.pack(anchor=tk.CENTER,expand=True)

        self.wd.mainloop()
#_________________Button functions

    def uploadPic(self):
        self.selectedPic=askopenfilename()
        self.cv_img = cv2.cvtColor(cv2.imread(self.selectedPic), cv2.COLOR_BGR2RGB)
        self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.cv_img))
        self.canvas.create_image(10, 50, image=self.photo, anchor=tk.NW)

    def triangulate(self):
        edges=self.detect_edges(self.selectedPic)
        al=Delaunay_Lawson(edges)
        ans=al.calculate()
        self.photo=self.apply_delaunay(self.selectedPic,ans,al)
        self.cv_img = cv2.cvtColor(self.photo, cv2.COLOR_BGR2RGB)
        self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.cv_img))
        self.canvas.create_image(10, 50, image=self.photo, anchor=tk.NW)

    def save(self):
        self.save=asksaveasfile(mode='w',defaultextension='.jpg')
        im=PIL.Image.fromarray(self.cv_img)
        im.save(self.save)


    # ___________________Image process_______________________________________
    def detect_edges(self,image, precise=0.0005, sigma=0.33):
        '''Return points on the edges of the pattern'''
        img = cv2.imread(image)
        height = img.shape[0]
        width = img.shape[1]
        v = np.median(img)
        low = int(min(0, (1 - sigma) * v))
        high = int(max(255, (1 + sigma) * v))
        edges = cv2.Canny(img, low, high)
        list = []
        for j in range(height - 2):
            for i in range(width - 2):
                if edges[j][i] == 255 and random.random() < precise:
                    list.append((i, j))
        list.extend([(0, 0), (0, height - 1), (width - 1, 0), (width - 1, height - 1)])
        return list

    def apply_delaunay(self,image, tris, al):
        '''Apply triangles to the image'''
        img = cv2.imread(image)
        for t in tris:
            x, y, r = al.getDic()[t]
            if int(y) < img.shape[0] and int(x) < img.shape[1]:
                r, g, b = img[int(y)][int(x)]
                cv2.fillPoly(img, [np.array(t)], color=(int(r), int(g), int(b)))
        # cv2.imshow("img", img)
        # cv2.waitKey(0)
        return img

if __name__ == '__main__':
    board=Board(tk.Tk(),"Image Processor")
