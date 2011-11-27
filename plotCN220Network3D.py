'''
@author Michael J Bommarito II
@contact michael.bommarito@gmail.com
@date Feb 21, 2011
@license Simplified BSD, (C) 2011.

Plot the network of the first 1000 #cn220 tweets with igraph and cairo.
'''

#Code originally from: http://www.michaelbommarito.com/blog/2011/02/21/plotting-3d-graphs-with-python-igraph-and-cairo-cn220-example/
#Modified slightly (thicker edges) by David Chudzicki

import cairo
import codecs
#import dateutil.parser
import igraph
import numpy
import re

def readTweets(fileName):
	'''
	Read in tweet data from the tab-delimited tweet format.
	'''
	rows = [[field.strip() for field in line.split("\t")] for line in codecs.open(fileName, 'r', 'utf-8')]
	return [(int(row[0]), dateutil.parser.parse(row[1]), row[2], row[3]) for row in rows]

def getNetwork(tweets):
	'''
	Parse the list of tweets and find "edges" embedded in the tweets.
	Edges are just mentions in the tweet text, e.g., @mjbommar.
	Then process the network from the edges.
	'''
	reMention = re.compile('\@([\w]+)')

	# Calculate the list of mentions
	mentions = []
	for tweet in tweets:
		mentions.extend([(tweet[1], tweet[2],  name) for name in reMention.findall(tweet[3])])
	
	# Sort by date
	mentions = sorted(mentions)
	
	# Now convert the dates/mention to edges and weights 
	dates, nodeA, nodeB = zip(*mentions)
	nodes = set(nodeA) | set(nodeB)
	nodes = sorted(list(nodes))
	nodeMap = dict([(v,i) for i,v in enumerate(nodes)])
	edges = [(nodeMap[e[1]], nodeMap[e[2]]) for e in mentions]
	edges, weights = map(list, zip(*[[e, edges.count(e)] for e in set(edges)]))
	
	# Now create the graph
	graph = igraph.Graph(edges)
	graph.es['weight'] = weights
	graph.vs['label'] = nodes
	
	return graph

def project2D(layout, alpha, beta):
	'''
	This method will project a set of points in 3D to 2D based on the given
	angles alpha and beta.
	'''
	
	# Calculate the rotation matrices based on the given angles.
	c = numpy.matrix([[1, 0, 0], [0, numpy.cos(alpha), numpy.sin(alpha)], [0, -numpy.sin(alpha), numpy.cos(alpha)]])
	c = c * numpy.matrix([[numpy.cos(beta), 0, -numpy.sin(beta)], [0, 1, 0], [numpy.sin(beta), 0, numpy.cos(beta)]])
	b = numpy.matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
	
	# Hit the layout, rotate, and kill a dimension
	layout = numpy.matrix(layout)
	X = (b * (c * layout.transpose())).transpose()
	return [[X[i,0],X[i,1],X[i,2]] for i in range(X.shape[0])]

def drawGraph3D(graph, layout, angle, fileName):
	'''
	Draw a graph in 3D with the given layout, angle, and filename.
	'''
	
	# Setup some vertex attributes and calculate the projection
	graph.vs['degree'] = graph.degree()
	vertexRadius = .1 * (0.9 * 0.9) / numpy.sqrt(graph.vcount())
	graph.vs['x3'], graph.vs['y3'], graph.vs['z3'] = zip(*layout)
	
	
	layout2D = project2D(layout, angle[0], angle[1])
	graph.vs['x2'], graph.vs['y2'], graph.vs['z2'] = zip(*layout2D)
	minX, maxX = min(graph.vs['x2']), max(graph.vs['x2'])
	minY, maxY = min(graph.vs['y2']), max(graph.vs['y2'])
	minZ, maxZ = min(graph.vs['z2']), max(graph.vs['z2'])
	
	# Calculate the draw order.  This is important if we want this to look
	# realistically 3D.
	zVal, zOrder = zip(*sorted(zip(graph.vs['z3'], range(graph.vcount()))))
	
	# Setup the cairo surface
	surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1280, 800)
	con = cairo.Context(surf)
	con.scale(1280.0, 800.0)
	
	# Draw the background
	con.set_source_rgba(0.0, 0.0, 0.0, 1.0)
	con.rectangle(0.0, 0.0, 1.0, 1.0)
	con.fill()
	
	# Draw the edges without respect to z-order but set their alpha along
	# a linear gradient to represent depth.
	for e in graph.get_edgelist():
		# Get the first vertex info
		v0 = graph.vs[e[0]]
		x0 = (v0['x2'] - minX) / (maxX - minX)
		y0 = (v0['y2'] - minY) / (maxY - minY)
		alpha0 = (v0['z2'] - minZ) / (maxZ - minZ)
		#alpha0 = max(.1, alpha0)
                alpha0 = 1
		
		# Get the second vertex info
		v1 = graph.vs[e[1]]
		x1 = (v1['x2'] - minX) / (maxX - minX)
		y1 = (v1['y2'] - minY) / (maxY - minY)
		alpha1 = (v1['z2'] - minZ) / (maxZ - minZ)	
		#alpha1 = max(0.1, alpha1)
                alpha1=1
		                
		# Setup the pattern info
		pat = cairo.LinearGradient(x0, y0, x1, y1)
		pat.add_color_stop_rgba(0, 1, 1.0, 1.0,  alpha0 / 6.0)
		pat.add_color_stop_rgba(1, 1, 1.0, 1.0,  alpha1 / 6.0)
		con.set_source(pat)
		
		# Draw the line
		con.set_line_width(vertexRadius * 4)
                
		con.move_to(x0, y0)		
		con.line_to(x1, y1)
		con.stroke()
	
	# Draw vertices in z-order
	for i in zOrder:
		v = graph.vs[i]
		alpha = (v['z2'] - minZ) / (maxZ - minZ)
		alpha = max(0.1, alpha)
		radius = vertexRadius
		x = (v['x2'] - minX) / (maxX - minX)
		y = (v['y2'] - minY) / (maxY - minY)
		
		# Setup the radial pattern for 3D lighting effect 
		pat = cairo.RadialGradient(x, y, radius / 4.0, x, y, radius)
		pat.add_color_stop_rgba(0, alpha, 0, 0, 1)
		pat.add_color_stop_rgba(1, 0, 0, 0, 1)
		con.set_source(pat)
		
		
		# Draw the vertex sphere
		con.move_to(x, y)
		con.arc(x, y, radius, 0, 2 * numpy.pi)	
		con.fill()
	
	# Output the surface
	surf.write_to_png(fileName)

def drawGraphFrames(graph, layout, directory, n=10):
	for frame in range(0,400,400/n):
		alpha = frame * numpy.pi / 200.
		beta = frame * numpy.pi / 150.
		print frame, alpha, beta
		drawGraph3D(graph, layout, (alpha, beta), directory + "/%08d.png" % (frame))
