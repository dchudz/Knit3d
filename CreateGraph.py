#Feel free to copy/modify, as long as you:
#  --attribute me by name (David Chudzicki)
#  --attribute me by URL (www.learnfromdata.com)
#  --leave this notice attached

from igraph import *
from plotCN220Network3D import *
import os

class KnittedGraph(Graph):
    def __init__(self):
        Graph.__init__(self,directed=True)
        self.vs[0]["row"] = 0
        self.current = int(0)
        self.direction = None

    def AddStitch(self,offsets = [1]):
        #add a stitch in same row
        #"offset" is offset in old row
        self.add_vertices(1)
        row = self.vs[self.current+1]["row"] = self.vs[self.current]["row"]
        max_edge_id = self.ecount()
        self.add_edges([(self.current,self.current+1)])
        self.es[max_edge_id]["type"] = "across"
        DownList =  [e.source for e in self.es if e.target==self.current and e["type"]=="up"]
        if len(DownList) > 0:
            if self.direction == "opposite":
                connections = [min(DownList) - offset for offset in offsets]
            elif self.direction == "same":
                connections = [max(DownList) + offset for offset in offsets]
            else:
                raise Exception("No good direction type")
            for connection in connections:
                self.add_edges([(connection,self.current+1)])
                max_edge_id = self.ecount()
                self.es[max_edge_id-1]["type"] = "up"
            self.vs[self.current+1]["row"] = max([self.vs[connection]["row"] for connection in connections]) + 1
        self.current+=1
        
    def AddStitches(self,n):        
        #add  n  stitches in same row
        for i in range(n):
            self.AddStitch()
            
    def NewRow(self):        
        #add  1  stitch in new row (back and forth)
        self.add_vertices(1)
        row = self.vs[self.current+1]["row"] = self.vs[self.current]["row"] + 1
        max_edge_id = self.ecount()
        self.add_edges([(self.current,self.current+1)])
        self.es[max_edge_id]["type"] = "up"
        self.direction = "opposite"
        self.current+=1
        
        
    def Increase(self):        
        #add stitch as an increase
        self.AddStitch()
        self.AddStitch(offsets=[0])
        
    def Decrease(self):        
        #add stitch as a decrease
        self.AddStitch(offsets = [1, 2])

    def FinishRow(self):
        #knit until end of row
        offset = 1
        while True:
            DownList =  [e.source for e in self.es if e.target==self.current and e["type"]=="up"]
            if len(DownList) > 0:
                if self.direction == "opposite":
                    connection = min(DownList) - offset
                elif self.direction == "same":
                    connection = max(DownList) + offset
                else:
                    raise Exception("No good direction type")
            if connection < 0 or self.vs[connection]["row"]  != self.vs[self.current]["row"] -1:
                break
            self.AddStitch()
        
    def AtRowEnd(self):
        #knit until end of row
        offset = 1
        DownList =  [e.source for e in self.es if e.target==self.current and e["type"]=="up"]
        if len(DownList) > 0:
            if self.direction == "opposite":
                connection = min(DownList) - offset
            elif self.direction == "same":
                connection = max(DownList) + offset
            else:
                raise Exception("No good direction type")
            if connection < 0 or self.vs[connection]["row"]  != self.vs[self.current]["row"] -1:
                return True
            else:
                return False

    def ConnectToZero(self):
        #for circular knitting
        self.direction = "same"
        max_edge_id = self.ecount()
        self.add_edges([(0,self.current)])        
        self.es[max_edge_id]["type"] = "up"
        self.vs[self.current]["row"] = 1

    def StitchesInPrevRow(self):
        return sum([row == self.vs[self.current]["row"] - 1 for row in self.vs["row"]])

def FlatKnitting(RowLength, NumRows):
    g = KnittedGraph()
    g.AddStitches(RowLength-1)
    for i in range(NumRows-1):
        g.NewRow()
        g.FinishRow()
    return g

def NegCurvature(RowLength, NumStitches):
    g = KnittedGraph()
    g.AddStitches(RowLength-1)
    g.NewRow()
    for i in range(2000):
        if g.AtRowEnd():
            g.NewRow()
        elif i % 3 == 0:
            g.Increase()
        else:
            g.AddStitch()



def hat(n,m):
    #pattern (approximately) from:
    #http://www.aokcorral.com/projects/how2sept2004.htm
    g = KnittedGraph() #now has one stitch
    g.AddStitches(n) # now has 97 stitches
    g.ConnectToZero()
    for i in range(m):
        g.AddStitch()
        g.FinishRow()
    while True:
        g.FinishRow()
        #g.AddStitch()
        #g.FinishRow()
        row = g.vs[g.current]["row"] + 1
        while True:
            g.AddStitches(3)
            g.AddStitch(offsets=[1,2,3])
            if g.vs[g.current]["row"] != row:
                break
        if g.StitchesInPrevRow()  < 10:
            break
    #bunch top together:
    row = g.vs[g.current]["row"]
    TopRow = [v.index for v in g.vs if v["row"] == row]
    for v in TopRow:
        for w in TopRow:
            print v
            print w
#            g.add_edges([(v,w)])
    return g


def cylinder(n=96, m=11):
    #http://alison.knitsmiths.us/pattern_beginners_hat.html
    g = KnittedGraph()
    g.AddStitches(n)
    g.ConnectToZero()
    for i in range(m):
        g.AddStitch()
        g.FinishRow()
    return g


def PseudoSphere(n,m):
    #n: number of stitches in initial row
    #m: number of stitches after first row
    g = KnittedGraph()
    g.AddStitches(n)
    g.ConnectToZero()
    for i in range(m):
        if g.AtRowEnd():
            g.NewRow()
        elif i % 3 == 0:
            g.Increase()
        else:
            g.AddStitch()
    return g

def movie(g, name, n=50):
    layout = g.layout("kk_3d")
    directory = "/home/ubuntu/dj/mysite/media/graphs/" + name + "/"
    os.system("mkdir " + directory)
    os.system("rm " + directory + "*")
    drawGraphFrames(g, layout, directory,n=n)
    os.system("convert -delay 20 " + directory + "*.png " + directory + "movie.gif")



def plot2d(g, directory = "/home/ubuntu/dj/mysite/media/graphs/", name = "plot2d.png"):
    color_dict = {"across": "blue", "up": "red"}
    g.es["color"] = [color_dict[type] for type in g.es["type"]]
    plot(g, directory + name, layout=g.layout("kk") )


g = KnittedGraph()
g.AddStitches(8)
g.ConnectToZero()
g.AddStitches(16)

#g.AddStitch()
#g.Decrease()

plot2d(g)



#drawGraph3D(g, g.layout("kk_3d"), (1,2), "/home/ubuntu/dj/mysite/media/graphs/plot3d.png")

#g = hat(100,20)
#movie(g,"hat_100_20_bunch")

#g = PseudoSphere(5,2000)
#plot2d(g)
#movie(g,"PseudoSphere_5_2000")

#g = cylinder(50,20)
#movie(g, "cylinder_50_20")

#g = FlatKnitting(50,20)
#movie(g, "flat_50_20")

#g = FlatKnitting(50,40)
#movie(g, "flat_50_40")
