from igraph import *
from plotCN220Network3D import *

class KnittedGraph(Graph):
    def __init__(self):
        Graph.__init__(self,directed=True)
        self.vs[0]["row"] = 0
        self.current = int(0)
        self.direction = None

    def AddStitch(self,offsets = 1):
        #add a stitch in same row
        #"offset" is offset in old row
        self.add_vertices(1)
        row = self.vs[self.current+1]["row"] = self.vs[self.current]["row"]
        max_edge_id = g.ecount()
        self.add_edges([(self.current,self.current+1)])
        g.es[max_edge_id]["type"] = "across"
        DownList =  [e.source for e in self.es if e.target==self.current and e["type"]=="up"]
        if len(DownList) > 0:
            if self.direction == "opposite":
                connection = min(DownList) - offset
            elif self.direction == "same":
                connection = max(DownList) + offset
            else:
                raise Exception("No good direction type")
            max_edge_id = g.ecount()
            self.add_edges([(connection,self.current+1)])
            g.es[max_edge_id]["type"] = "up"
     
        self.current+=1
        
    def AddStitches(self,n):        
        #add  n  stitches in same row
        for i in range(n):
            self.AddStitch()
            
    def NewRow(self):        
        #add  1  stitch in new row (back and forth)
        self.add_vertices(1)
        row = self.vs[self.current+1]["row"] = self.vs[self.current]["row"] + 1
        max_edge_id = g.ecount()
        self.add_edges([(self.current,self.current+1)])
        g.es[max_edge_id]["type"] = "up"
        self.direction = "opposite"
        self.current+=1
        
        
    def Increase(self):        
        #add stitch as an increase
        self.AddStitch()
        self.AddStitch(offset=0)
        
    def Decrease(self):        
        #add stitch as a decrease
        

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
        max_edge_id = g.ecount()
        self.add_edges([(0,self.current)])        
        g.es[max_edge_id]["type"] = "up"



def FlatKnitting(RowLength, NumRows):
    g = KnittedGraph()
    g.AddStitches(RowLength-1)
    for i in range(NumRows-1):
        g.NewRow()
        g.FinishRow()

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




g = KnittedGraph()
g.AddStitches(30)
g.ConnectToZero()
g.AddStitches(600)

color_dict = {"across": "blue", "up": "red"}
g.es["color"] = [color_dict[type] for type in g.es["type"]]

plot(g, "/home/ubuntu/dj/mysite/media/graphs/plot2d.png", layout=g.layout("kk") )



#drawGraph3D(g, g.layout("kk_3d"), (1,2), "/home/ubuntu/dj/mysite/media/graphs/plot3d.png")
layout = g.layout("kk_3d")
directory = "/home/ubuntu/dj/mysite/media/graphs/cylinder/"
drawGraphFrames(g, layout, directory,n=100)

