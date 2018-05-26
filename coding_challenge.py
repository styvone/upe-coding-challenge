# import the requests, re, string, json libraries
import requests
import re
import string
import json

# API-endpoint; my awesome key is UE0XI
URL = "http://upe.42069.fun/UE0XI"

# list of already-guessed characters in the game
ALREADY_GUESSED = []

# most common letters (left to right)
MASTER = "etaoinsrhldcumfpgwybvkxjqz"

# function to change a string like "___" to "[a-z][a-z][a-z]" (RegEx)
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

# returns next most common letter from MASTER (takes into account the already guessed characters)
def mostCommon():
	for i in MASTER:
		if i not in ALREADY_GUESSED:
			return i

# function to return educated guesses based on current game state
def educatedGuess(stateString):
	# list to hold our current words (from game state)
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
			elif (m == '+'):
				n = n.replace('+', '')
			elif (m == '"'):
				n = n.replace('"', '')
			elif (m == ']'):
				n = n.replace(']', '')
			elif (m == '['):
				n = n.replace('[', '')
			elif (m == '*'):
				n = n.replace('*', '')
			elif (m == '}'):
				n = n.replace('}', '')
			elif (m == '{'):
				n = n.replace('{', '')
		currentWords.append(n)
	# list to hold all possible words that could be in the current state string
	possibleWords = []
	# for every single word in the game,
	for i in currentWords:
		# look through entire dictionary
		for j in open("newDict.txt", 'r'):
			searchObj = re.search(r'^' + changeRegEx(i) + r'$', str.lower(str(j)))
			# we found possible matches --> put them into possibleWords list
			if searchObj:
				possibleWords.append(searchObj.group())
	# what if we dont find any matching words? --> should return next most common char
	if not possibleWords:
		c = mostCommon()
		return c
	else:
		# possibleWords is not empty
		# dictionary to store most frequent characters, calculated from possibleWords list
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
		# now freqList contains frequency listing of all possible characters to choose from
		# we must sort freqList --> put results into finalList
		finalList = []
		for key, value in sorted(freqList.iteritems(), key=lambda (k,v): (v,k)):
			finalList.append(key)
		finalList.reverse()
		# return the most frequently appearing character (first entry in list)
		if finalList:
			z = finalList[0]
		else:
			z = mostCommon()
		return z

# function to add words not previously seen to my dictionary
def updateDict(lyricString):
	# a list to hold current lyrics
	currentLyrics = []
	# for each lyric,
	for n in lyricString.split():
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
			elif (m == '+'):
				n = n.replace('+', '')
			elif (m == '"'):
				n = n.replace('"', '')
			elif (m == ']'):
				n = n.replace(']', '')
			elif (m == '['):
				n = n.replace('[', '')
			elif (m == '*'):
				n = n.replace('*', '')
			elif (m == '}'):
				n = n.replace('}', '')
			elif (m == '{'):
				n = n.replace('{', '')
		currentLyrics.append(n)
	# for each lyric,
	for i in currentLyrics:
		# flag to see if lyric is in dictionary
		inDict = False
		# look through dictionary for that lyric word
		for j in open("newDict.txt", 'r'):
			searchObj = re.search(r'^' + i + r'$', str.lower(str(j)))
			# if we did find it in dictionary, set the flag
			if searchObj:
				inDict = True
		# if we didn't find the lyric in our dictionary,
		if inDict == False:
			f = open("newDict.txt", 'a')
			# append to end of dictionary
			f.write((i.decode("utf-8").encode("utf-8"))+'\n')
			f.close()

# main loop
while (True):
	# start the game
	r = requests.get(URL)
	playingGame = r.json()
	# check to see if Neo already got finessed OR is finessing
	# if so, restart a new game to get another Neo
	if (((playingGame['status']).encode("utf-8")) == 'DEAD' or ((playingGame['status']).encode("utf-8")) == 'FREE'):
		updateDict((playingGame['lyrics']).encode("utf-8"))
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
			updateDict((playingGame['lyrics']).encode("utf-8"))
			break
		elif (((playingGame['status']).encode("utf-8")) == 'FREE'):
			print "GAME-OVER: YOU WON!"
			updateDict((playingGame['lyrics']).encode("utf-8"))
			break
	print "Win rate: " + (str(playingGame['win_rate'])) + "\n" + "# of games played: " + (str(playingGame['games']))
	ALREADY_GUESSED[:] = []