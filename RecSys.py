# calculate recommendations at selected location for chosen emotion (pleasure and activity values) and picture database, real or random
import sys # example usage: RecSys.py 48.137079 11.576006 2 2 static/local.csv false
import numpy as np
import csv
from sklearn.neighbors import NearestNeighbors
from random import sample

# info: save all parameters, create arrays
# dataset record = picture, dataset features = latitude, longitude, pleasure, activity
gpsPos = [[sys.argv[1],sys.argv[2]]] # user data
paVal = [[sys.argv[3],sys.argv[4]]] # user data
db = sys.argv[5]
rand = sys.argv[6] # real or random recommendations (pleasure and activity values used or not; for demonstration purposes only)
fileNumber = sum(1 for line in open(db)) # number of pictures
closeNumber = 50 # number of closest pictures to be considered

# np.set_printoptions(threshold=np.nan) # no truncating of matrices
gpsA = np.zeros(shape=(fileNumber,2)) # array for gps data
paA = np.zeros(shape=(closeNumber,2)) # array for pleasure and activity data
# gpsA = np.array([[48.137079, 11.576006]])

# close: fill gps data array, calculate 50 closest recommendations
with open(db, 'r', newline='') as csvIn: # row_count = sum(1 for row in csvIn)
	database = csv.reader(csvIn)
	for counterGPS, row in enumerate(database):
		gpsA[counterGPS] = row[3], row[4] # fill array
# print(gpsA)

# k-nearest neighbor for gps data
# fit nearest neighbor object to dataset: check gps data
gpsNeighbors = NearestNeighbors(n_neighbors=closeNumber, algorithm='ball_tree').fit(gpsA)
# find k-neighbors of each point in dataset by calling kneighbors()
gpsDistances, gpsIndices = gpsNeighbors.kneighbors(gpsA) # optional step
# print distances and indices of k-nearest neighbors for each record in dataset
# print(gpsDistances)
# print(gpsIndices)
# produce sparse graph showing connections between neighboring points
# print(gpsNeighbors.kneighbors_graph(gpsA).toarray())
# find k-neighbors of user's location, return only indices, select closeNumber closest
closeResults = gpsNeighbors.kneighbors(gpsPos, return_distance=False) # picture indices, sorted after closeness to location
# print(closeResults)

# top: fill pleasure and activity data array, calculate 3 best recommendations
info = [] # array with all information about close pictures
with open(db, 'r', newline='') as csvIn:
	database = csv.reader(csvIn)
	gpsRows = [row for elem, row in enumerate(database) if elem in (closeResults[0])] # consider only closest pictures
	for counterPA, row in enumerate(gpsRows):
		paA[counterPA] = row[6], row[7] # fill array
		info.append(','.join(row)) # close picture information, sorted in order of appearance in database, separated with comma
# print(paA)

# k-nearest neighbor for pleasure and activity data
paNeighbors = NearestNeighbors(n_neighbors=3, algorithm='ball_tree').fit(paA)
paDistances, paIndices = paNeighbors.kneighbors(paA) # optional step
# print(paDistances)
# print(paIndices)
# print(paNeighbors.kneighbors_graph(paA).toarray())
# find k-neighbors of user's emotion, return only indices, select 3 best
topThree = paNeighbors.kneighbors(paVal, return_distance=False) # picture indices, sorted after closeness to emotion
# print(topThree)

# prepare: convert recommendation data for proper representation
closeIndices = str(closeResults.tolist()).replace(',','') # tolist: fix for numpy adding a newline after a certain length
randints = sample(range(50),3) # three distinct random integers from 0-49
topInfo = str(info[topThree[0][0]])+'\n'+str(info[topThree[0][1]])+'\n'+str(info[topThree[0][2]]) if rand == 'false' else str(info[randints[0]]+'\n'+info[randints[1]]+'\n'+info[randints[2]]) # info instead of closeResults[0] because of different sorting
print(closeIndices[2:len(closeIndices)-2]+'...'+topInfo) # close picture indices (without [[]]) and top picture information are returned