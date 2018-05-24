# import the requests, re, string, json, ast libraries
import requests
import re
import string
import json
import ast

# API-endpoint; my awesome key is UE0XI
URL = "http://upe.42069.fun/UE0XI"

# list of already-guessed characters
ALREADY_GUESSED = []

# most common letters (left to right)
MASTER = "'esiarntolcdupmghbyfvkwzxqj'"

# function to change a string like "___" to "[a-z][a-z][a-z]"
def changeRegEx(word):
	regExString = ""
	for i in ALREADY_GUESSED:
		regExString = regExString + i
	if regExString:
		compareMe = "(?![" + regExString + "])[a-z]"
	else:
		compareMe = "[a-z]"
	newString = re.sub("_", compareMe, str(word), 0, 0)
	return newString

# returns most common letter (takes into account the already guessed characters)
def mostCommon():
	for i in MASTER:
		if i not in ALREADY_GUESSED:
			return i

# function to return educated guesses based on current state string
def educatedGuess(stateString):
	# dictionary to keep track of { (# of '_'s): "selected char" }
	findShort = {}
	# an array to hold our current words
	currentWords = []
	# for every input word, take out ending punctuation since our dictionary doesn't recognize these
	for n in stateString.split():
		for m in n:
				if (m == '.'):
					n = n.replace('.', '')
				elif (m == ','):
					n = n.replace(',', '')
				elif (m == ':'):
					n = n.replace(':', '')
				elif (m == '!'):
					n = n.replace('!', '')
				elif (m == '?'):
					n = n.replace('?', '')
				elif (m == ';'):
					n = n.replace(';', '')
		currentWords.append(n)

	# for debugging purposes...
	printMe = []
	for x in currentWords:
		printMe.append(x.encode("utf-8"))
	print "CURRENT STATE: ", printMe

	# for every single word,
	for i in currentWords:
		# list to hold all possible words that the current word under inspection could be
		possibleWords = []
		# look through entire dictionary
		for j in open("newDict.txt", 'r'):
			searchObj = re.search(r'^' + changeRegEx(i) + r'$', str.lower(str(j)))
			# we found possible matches --> put them into possibleWords list
			if searchObj:
				possibleWords.append(searchObj.group())
		# what if we dont find ANY matching words? --> should return most common char
		if not possibleWords:
			c = mostCommon()
			findShort[c] = i.count("_")
			# break out of while loop --> continue to next word in state string
			break
		else:
			# possibleWords is NOT empty --> we found some possible words
			# another dictionary to store most frequent characters, calculated from possibleWords
			freqList = {}
			# for each possible word,
			for q in possibleWords:
				# for each character in that possible word,
				for w in q:
					if (w not in ALREADY_GUESSED) and (w.isalpha()):
						# add character frequencies to dict
						if w in freqList:
							freqList[w] += 1
						else:
							freqList[w] = 1
			# CHECK TO SEE IF FREQLIST IS EMPTY --> means the word is already filled in --> go to next word in state
			if not freqList:
				continue
			else:
				# now, freqList contains frequency listing of all possible characters to choose from
				# we must sort freqList to get finalList
				finalList = []
				for key, value in sorted(freqList.iteritems(), key=lambda (k,v): (v,k)):
					finalList.append(key)
				finalList.reverse()
				# get most frequent character from finalList and put into findShort
				for z in finalList:
					if (z not in ALREADY_GUESSED) and (z.isalpha()):
						findShort[z] = i.count("_")
						break
	if findShort:
		# remove dictionary keys with values of 0 (meaning they're already filled in)
		for key in findShort.keys():
			if findShort[key] == 0:
				del findShort[key]
		# sort the contents of the dictionary into a new list sortedList
		sortedList = []
		for key, value in sorted(findShort.iteritems(), key=lambda (k,v): (v,k)):
			sortedList.append(key)
		# Now, sortedList has the characters to guess in order from left to right --> just take first entry
		result = sortedList[0]
	else:
		# if we don't have anything to make an educated guess from --> get most common char
		result = mostCommon()
	return result

# main loop
while (True):
	# start the game
	r = requests.get(URL)
	if r.status_code != 200:
		playingGame = ast.literal_eval((r.text).encode("utf-8"))
	else:
		playingGame = r.json()
	# check to see if Neo already got finessed OR is finessing
	# if so, restart a new game to get another Neo
	if (((playingGame['status']).encode("utf-8")) == 'DEAD' or ((playingGame['status']).encode("utf-8")) == 'FREE'):
		continue
	# Neo must be still ALIVE at this point --> let's make educated guesses
	# external counter
	begin = 0
	while (True):
		goodGuess = ''
		# we'll guess 'a' and 'e' first to get our words warmed up
		if begin == 0:
			goodGuess = 'a'
			begin += 1
		elif begin == 1:
			goodGuess = 'e'
			begin += 1
		else:
			goodGuess = educatedGuess((playingGame['state']).encode("utf-8"))
		data = { "guess" : goodGuess }
		ALREADY_GUESSED.append(goodGuess)
		r = requests.post(URL, data)
		if r.status_code != 200:
			playingGame = ast.literal_eval((r.text).encode("utf-8"))
		else:
			playingGame = r.json()
		if (((playingGame['status']).encode("utf-8")) == 'DEAD'):
			print "GAME-OVER: YOU LOST!"
			break
		elif (((playingGame['status']).encode("utf-8")) == 'FREE'):
			print "GAME-OVER: YOU WON!"
			break
	print "Win rate: " + (str(playingGame['win_rate'])) + "\n" + "# of games played: " + (str(playingGame['games']))
	ALREADY_GUESSED[:] = []