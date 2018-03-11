# tag own picture database
def photoToEmotion(photo):
	# predict: get response from Clarifai API request with concepts (limit maximum number) and parse as json
	import json
	from clarifai.rest import ClarifaiApp

	CLARIFAI_API_KEY = ''
	conceptsNumber = 10
	cApp = ClarifaiApp(api_key = CLARIFAI_API_KEY)
	model = cApp.models.get('general-v1.3') # 'travel-v1.0' needs word.lower() because API returns capitalized words
	result = model.predict_by_filename(photo, max_concepts = conceptsNumber) # predict_by_filename for photos stored locally
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

# parse: add concepts, pleasure, activity and emotion, save as csv
import csv
with open('example/db-untagged.csv', 'r', newline='') as csvIn, open('example/db.csv', 'w') as csvOut:
	database = csv.reader(csvIn)
	writer = csv.writer(csvOut, lineterminator='\n')
	for count, row in enumerate(database):
		final = photoToEmotion('example/'+row[0]) # call photoToEmotion for each file
		row.append(final[0]) # concepts
		row.append(final[1]) # pleasure
		row.append(final[2]) # activity
		row.append(final[3]) # emotion
		writer.writerow(row)
		print('Picture ' + str((count+1)) + ' tagged!')
print('Finished! Data written to db.csv.')