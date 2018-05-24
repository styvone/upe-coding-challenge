# import the requests, re, string, json libraries
import requests
import re
import string
import json

# API-endpoint; my awesome key is UE0XI
URL = "http://upe.42069.fun/UE0XI"

# list of already-guessed characters in the game
ALREADY_GUESSED = []

# list of candidate letters (during each run of making an educated guess)
TEMP = []

# most common letters (left to right)
MASTER = "esiarntolcdupmghbyfvkwzxqj"

# function to change a string like "___" to "[a-z][a-z][a-z]" (reg-ex)
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

# returns next most common letter from MASTER (takes into account the already considered characters)
def mostCommon(tempList):
	for i in MASTER:
		if i not in tempList:
			return i

# function to return educated guesses based on current game state
def educatedGuess(stateString):
	# dictionary to keep track of entries of the form { "selected char": (# of '_'s) }
	findShort = {}
	# an array to hold our current words (from game state)
	currentWords = []
	print "CURRENT STATE: ", stateString.split()
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
			elif (m == '('):
				n = n.replace('(', '')
			elif (m == ')'):
				n = n.replace(')', '')
		currentWords.append(n)
	# get a copy of ALREADY_GUESSED characters in game
	TEMP = ALREADY_GUESSED[:]
	# for every single word in the game,
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
			c = mostCommon(TEMP)
			findShort[c] = i.count("_")
			TEMP.append(c)
		else:
			# possibleWords is NOT empty --> we found some possible words
			# another dictionary to store most frequent characters, calculated from possibleWords list
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
				# we must sort freqList --> use finalList
				finalList = []
				for key, value in sorted(freqList.iteritems(), key=lambda (k,v): (v,k)):
					finalList.append(key)
				finalList.reverse()
				# get most frequent character from finalList and put into findShort
				for z in finalList:
					if (z not in TEMP) and (z.isalpha()):
						findShort[z] = i.count("_")
						TEMP.append(z)
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
		result = mostCommon(ALREADY_GUESSED)
	return result

# main loop
while (True):
	# start the game
	r = requests.get(URL)
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
		print "GUESS: ", goodGuess
		r = requests.post(URL, data)
		playingGame = r.json()
		if (((playingGame['status']).encode("utf-8")) == 'DEAD'):
			print "GAME-OVER: YOU LOST!"
			break
		elif (((playingGame['status']).encode("utf-8")) == 'FREE'):
			print "GAME-OVER: YOU WON!"
			break
	print "Win rate: " + (str(playingGame['win_rate'])) + "\n" + "# of games played: " + (str(playingGame['games']))
	ALREADY_GUESSED[:] = []