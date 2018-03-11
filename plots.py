import csv
import numpy as np
from scipy import cluster
from matplotlib import pyplot

# copying of data into numpy array
paA = np.zeros(shape=(642,2)) # (250,2)
with open('static/local.csv', 'r', newline='') as csvIn: # static/flickr.csv
	database = csv.reader(csvIn)
	for counterPA, row in enumerate(database):
		paA[counterPA] = row[6], row[7]

vector = [cluster.vq.kmeans(paA, i) for i in range(1,10)] # k-means algorithm for k=1 to k=10

pyplot.plot([var for (cent, var) in vector]) # plot variance
pyplot.show()

cent, var = vector[8] # 9 clusters
colors, cdist = cluster.vq.vq(paA, cent) # vector quantization
pyplot.figure(figsize=(4,4))
pyplot.scatter(paA[:,0], paA[:,1], c=colors) # plot clusters
pyplot.xlim(1,3)
pyplot.ylim(1,3)
pyplot.savefig('kMeans.svg')
pyplot.savefig('kMeans.png', dpi=192)
pyplot.scatter(cent[:,0], cent[:,1], c='red') # plot centroids
pyplot.savefig('kMeans-cent.svg')
pyplot.savefig('kMeans-cent.png', dpi=192)
pyplot.show()

pyplot.figure(figsize=(5,4))
pyplot.hist2d(paA[:,0], paA[:,1], bins=20, range=[[1,3],[1,3]]) # plot histogram
pyplot.colorbar()
pyplot.savefig('hist.png', dpi=192)
pyplot.show()

pyplot.figure(figsize=(5,4))
pyplot.hist2d(paA[:,0], paA[:,1], bins=20, range=[[1.5,2.5],[1.5,2.5]]) # plot zoomed histogram
pyplot.colorbar()
pyplot.savefig('hist-zoom.png', dpi=192)
pyplot.show()