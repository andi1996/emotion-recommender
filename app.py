from flask import Flask, request, redirect, url_for
from flask_cors import CORS
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 # cached files expire immediately (only when modified through server); helpful for testing purposes
CORS(app) # Cross-Origin Resource Sharing allowed
	
@app.route('/getFile/')
def func():
	return redirect(url_for('static', filename=request.args.get('file'))) # helper function needed to be able to correctly access files via Flask
	
@app.route('/xml/')
def xmlParser():
	import requests
	import xml.etree.ElementTree as ET
	# import pprint

	# api: get response from Flickr API request
	FLICKR_API_KEY = ''
	lat = request.args.get('lat')
	lng = request.args.get('lng')
	picNumber = 100
	url = 'https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key='+FLICKR_API_KEY+'&sort=date-taken-desc&has_geo=1&lat='+str(lat)+'&lon='+str(lng)+'&radius=20&extras=date_taken,geo,url_l&per_page='+str(picNumber)+'&format=rest&page=1'
	response = requests.get(url)
	# with open('flickr.xml', 'wb') as file:
	# 	file.write(response.content)
	# tree = ET.parse('flickr.xml')

	# parse: parse response as xml
	tree = ET.ElementTree(ET.fromstring(response.content))
	root = tree.getroot()
	pic = root[0] # pic.attrib['pages'], pic.attrib['total']
	# links = open('links.txt', 'w')
	if len(pic) < picNumber: return 'Not enough pictures here!'

	def photoToEmotion(photo):
		# predict: get response from Clarifai API request with concepts (limit maximum number) and parse as json
		import json
		from clarifai.rest import ClarifaiApp

		CLARIFAI_API_KEY = ''
		conceptsNumber = 10
		cApp = ClarifaiApp(api_key = CLARIFAI_API_KEY)
		model = cApp.models.get('general-v1.3') # 'travel-v1.0' needs word.lower() because API returns capitalized words
		result = model.predict_by_url(photo, max_concepts = conceptsNumber) # predict_by_filename for photos stored locally
		# cApp.tag_urls([urls]) # tag_files
		datax = json.dumps(result)
		data = json.loads(datax)
		# print(datax, file = open('response.json', 'w'))
		# data = json.load(open('response.json'))

		# concepts: select concepts from json response
		concepts = ''
		conceptsList = ''
		answers = [] # array with return values
		for i in range(conceptsNumber-1):
			concepts += data['outputs'][0]['data']['concepts'][i]['name']+'\n'
			conceptsList += data['outputs'][0]['data']['concepts'][i]['name']+', '
		concepts += data['outputs'][0]['data']['concepts'][conceptsNumber-1]['name']
		conceptsList += data['outputs'][0]['data']['concepts'][conceptsNumber-1]['name']
		answers.append(conceptsList)
		# print(concepts)

		# search: look into dictionary and calculate average of the values for pleasure and activity
		counter = 0 # number of hits for words
		p = 0.0000 # pleasure score
		a = 0.0000 # activity score
		for line in concepts.split('\n'):
			word = line.split(' ', 1)[0] # cut off everything after first word
			# print(word)
			# look for a word in the dictionary and add values for pleasure and activity, if present
			with open('static/dict.txt') as dict:
				for line in dict:
					hit = line.split(' ', 1)[0]
					if word == hit:
						counter += 1
						p += float(line[40:46])
						a += float(line[50:56])
						# print(counter, p, a, line [40:46], line[50:56])
		p = 0 if counter == 0 else p/counter # average value; if no hits in dictionary found, set values to 0
		a = 0 if counter == 0 else a/counter
		answers.append(str(round(p,4)))
		answers.append(str(round(a,4)))
		# print(p, a)

		# eval: evaluate and get emotion for values of p and a: assign one of 16 affect words as the picture's emotion tag; not used any more for recommendations and left here for demonstration purposes only
		def getEmotion(p,a):
			if p>=1 and p<2 and a>=2.75 and a<=3:
				return 'tense'
			elif p>=1 and p<2 and a>=2.5 and a<2.75:
				return 'nervous'
			elif p>=1 and p<2 and a>=2.25 and a<2.5:
				return 'stressed'
			elif p>=1 and p<2 and a>=2 and a<2.25:
				return 'upset'
			elif p>=1 and p<2 and a>=1.75 and a<2:
				return 'miserable'
			elif p>=1 and p<2 and a>=1.5 and a<1.75:
				return 'sad'
			elif p>=1 and p<2 and a>=1.25 and a<1.5:
				return 'depressed'
			elif p>=1 and p<2 and a>=1 and a<1.25:
				return 'bored'
			elif p>=2 and p<=3 and a>=2.75 and a<=3:
				return 'alert'
			elif p>=2 and p<=3 and a>=2.5 and a<2.75:
				return 'excited'
			elif p>=2 and p<=3 and a>=2.25 and a<2.5:
				return 'elated'
			elif p>=2 and p<=3 and a>=2 and a<2.25:
				return 'happy'
			elif p>=2 and p<=3 and a>=1.75 and a<2:
				return 'contented'
			elif p>=2 and p<=3 and a>=1.5 and a<1.75:
				return 'serene'
			elif p>=2 and p<=3 and a>=1.25 and a<1.5:
				return 'relaxed'
			elif p>=2 and p<=3 and a>=1 and a<1.25:
				return 'calm'
			else:
				return 'undefined'
		emotion = getEmotion(p,a)
		answers.append(emotion)
		# print(emotion)
		return answers

	# parse (cont.): remove unnecessary attributes, add concepts, pleasure, activity and emotion, save as csv
	piclib = open('static/flickr-own.csv', 'w')
	for i in range(picNumber):
		# pprint(pic[i].get('url_l'), links) # .get('x') == .attrib['x']
		# removing unnecessary attributes; attributes are sorted alphabetically and therefore ordered differently from original API call; place_id, woeid, height_l, width_l and url_l might not be present
		del pic[i].attrib['id'], pic[i].attrib['owner'], pic[i].attrib['secret'], pic[i].attrib['server'], pic[i].attrib['farm'], pic[i].attrib['title'], pic[i].attrib['ispublic'], pic[i].attrib['isfriend'], pic[i].attrib['isfamily'], pic[i].attrib['datetakengranularity'], pic[i].attrib['datetakenunknown'], pic[i].attrib['accuracy'], pic[i].attrib['context'], pic[i].attrib['geo_is_family'], pic[i].attrib['geo_is_friend'], pic[i].attrib['geo_is_contact'], pic[i].attrib['geo_is_public']
		if 'place_id' in pic[i].attrib: del pic[i].attrib['place_id'] # after context
		if 'woeid' in pic[i].attrib: del pic[i].attrib['woeid'] # before geo_is_family
		if 'height_l' in pic[i].attrib: del pic[i].attrib['height_l']
		if 'width_l' in pic[i].attrib: del pic[i].attrib['width_l']
		url_l = pic[i].attrib['url_l'] if 'url_l' in pic[i].attrib else 'https://upload.wikimedia.org/wikipedia/en/4/48/Blank.JPG' # blank picture if no url provided
		final = photoToEmotion(url_l) # call photoToEmotion for each url
		# pic[i].set('concepts', final[0])
		# pic[i].set('pleasure', final[1])
		# pic[i].set('activity', final[2])
		# pic[i].set('emotion', final[3])
		datetaken = pic[i].attrib['datetaken']
		date = datetaken[0:4]+':'+datetaken[5:7]+':'+datetaken[8:10]+','+datetaken[11:19] # convert datetaken to specific format
		csvLine = url_l+','+date+','+pic[i].attrib['latitude']+','+pic[i].attrib['longitude']+',\"'+final[0]+'\",'+final[1]+','+final[2]+','+final[3] # concepts, pleasure, activity, emotion
		if i == picNumber-1: piclib.write(csvLine) # no newline when last picture reached
		else: piclib.write(csvLine+'\n')
		print('Picture ' + str((i+1)) + ' tagged!')
	# tree.write('flickr.xml')
	return 'Finished! Data written to flickr-own.csv.'

@app.route('/rec/')
def RecSys():
	import numpy as np
	import csv
	from sklearn.neighbors import NearestNeighbors
	from random import sample

	# info: save all parameters, create arrays
	# dataset record = picture, dataset features = latitude, longitude, pleasure, activity
	gpsPos = [[request.args.get('lat'),request.args.get('lng')]] # user data
	paVal = [[request.args.get('p'),request.args.get('a')]] # user data
	db = request.args.get('file')
	rand = request.args.get('rand') # real or random recommendations (pleasure and activity values used or not; for demonstration purposes only)
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
	return closeIndices[2:len(closeIndices)-2]+'...'+topInfo # close picture indices (without [[]]) and top picture information are returned

if __name__ == '__main__':
    app.run()