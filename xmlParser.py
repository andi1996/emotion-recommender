# create own Flickr picture database at selected location
import sys # example usage: xmlParser.py 48.137079 11.576006
import requests
import xml.etree.ElementTree as ET
# import pprint

# api: get response from Flickr API request
FLICKR_API_KEY = ''
lat = sys.argv[1]
lng = sys.argv[2]
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
if len(pic) < picNumber: sys.exit('Not enough pictures here!')

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
piclib = open('flickr.csv', 'w')
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
print('Finished! Data written to flickr.csv.')