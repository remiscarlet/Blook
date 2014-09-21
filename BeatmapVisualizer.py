#######################################
###### Main file for WaterEmblem ######
#######################################
import os
import pygame
import random
import sounds
import string
import time

#############################
###### Primary Class ########
#############################
class BeatmapVisualizer(object):
	############################
	###### Initialisation ######
	############################
	def __init__(self, win):
		self.init(win)

	def init(self, win):
		self.varInit(win)
		self.loadMap()
		self.fontInit()
		self.preGuiInit()
		self.guiInit()
		self.soundInit()
		self.keyInit()
		self.spriteInit()

	def varInit(self, win):
		self.currentBeatGrid = [[0,0,0,0,0,0],
								[0,0,0,0,0,0],
								[0,0,0,0,0,0],
								[0,0,0,0,0,0]]
		self.currentBeat = "1:1:1"
		self.isRunning = True
		self.trueWidth = 640#int(screenSize[0])
		self.trueHeight = 480#int(screenSize[1])
		self.width,self.height = 640,480
		self.clock = pygame.time.Clock()
		self.ticks = 0 #Used for general events
		self.win = win
		self.status = {"menu":False, "mapping":True, "playback":False}
		self.top = 20#px
		self.left = 20#px
		self.bot = 420#px
		self.right = 620#px
		self.height = 400#px
		self.length = 600#px
		self.textY = 420#px
		self.textX = 20#px
		self.tempo = 175#bpm

	def loadMap(self):
		self.notes = dict()
		#bm = open("beatmap.txt","wb")
		with open("beatmap.txt","r") as f:
			#format for line should be (measure:beat:subbeat,x,y)
			#subbeat should be in 16ths. Eg, the 3rd 16th on beat 2 of measure 5 would be (5:2:3)
			for line in f:
				if line[0] != "@":
					if line != "\n":
						line = line.replace(")","").replace("(","").replace("\n","").replace("\"","")
						line = line.split(",")
						time = line[0]
						val = [(int(line[1]),int(line[2]))]
						if time in self.notes:
							val.extend(self.notes[time])
						self.notes[time] = val
		self.clearBeatGrid()
		if self.notes.get(self.currentBeat) != None:
			beats = self.notes[self.currentBeat]
			for beat in beats:
				self.currentBeatGrid[beat[1]][beat[0]] = 1
	def clearBeatGrid(self):
		self.currentBeatGrid = [[0,0,0,0,0,0],
								[0,0,0,0,0,0],
								[0,0,0,0,0,0],
								[0,0,0,0,0,0]]
	#time is string measure:beat:subbeat
	#coords is tuple of (x,y)
	def writeMap(self,time,coords):
		if self.notes.get(self.currentBeat) != None and coords not in self.notes[time]:
			print "WRITE"
			fin = open("beatmap.txt","rt")
			content = fin.read()
			fout = open("temp.txt","wt")
			fout.write(content)
			line = "(\""+str(time)+"\","+str(coords[0])+","+str(coords[1])+")\n"
			fout.write(line)
			fout.close()
			fin.close()
			os.remove("beatmap.txt")
			os.rename("temp.txt","beatmap.txt")
			self.loadMap()

	def removeMap(self,time,coords):
		if self.notes.get(self.currentBeat) != None:
			fin = open("beatmap.txt","rt")
			content = fin.read()
			fout = open("temp.txt","wt")
			searchLine = "(\""+str(time)+"\","+str(coords[0])+","+str(coords[1])+")\n"
			print "SEARCHLINE", searchLine
			start = string.find(content, searchLine)-1
			end = start+len(searchLine)
			part1 = content[:start]
			part2 = content[end:]
			fout.write(part1+part2)
			fout.close()
			fin.close()
			os.remove("beatmap.txt")
			os.rename("temp.txt","beatmap.txt")
			if self.notes.get(self.currentBeat) != None:
				self.loadMap()

	def fontInit(self):
		self.dialogueFont = pygame.font.Font(os.path.join(os.path.curdir,'fonts','LTYPE.TTF'), 16)
		self.statFont = pygame.font.Font(os.path.join(os.path.curdir,'fonts','LTYPE.TTF'), 14)
		self.bigFont = pygame.font.Font(os.path.join(os.path.curdir,'fonts','LTYPE.TTF'), 20)


	def preGuiInit(self):
		pass
	############################################################################
	########### Entire below code should be looked at after UI is finalized ####
	############################################################################
	def guiInit(self):
		self.approachBox = pygame.Surface((100,100))
		self.approachBox.fill((100,100,100))

	def soundInit(self):
		self.bgm = sounds.BGM()
		self.sfx = sounds.SFX()
		self.music = os.path.join('M-Project_-_Kidz_War_2013-soundcloud-84530036.ogg')

	def keyInit(self):
		self.confirmHeld = False
		self.cancelHeld = False
		self.leftKey = int(pygame.K_LEFT)
		self.rightKey = int(pygame.K_RIGHT)
		self.upKey = int(pygame.K_UP)
		self.downKey = int(pygame.K_DOWN)
		self.confirmKey = int(pygame.K_RETURN)
		self.cancelKey = int(pygame.K_ESCAPE)
		self.pKey = int(pygame.K_p)
		self.shiftKey = int(pygame.K_LSHIFT)
		self.eKey = int(pygame.K_e)
		pygame.key.set_repeat(100, 50)

	def spriteInit(self):
		self.playerUIGroup = pygame.sprite.Group()

	#############################
	###### Events Handling ######
	#############################

	def events(self):
		#Because the gameplay requires constant stream of keypress
		#information, continuously send anyway.
		self.playingUpdate()
		#for all other events
		for event in pygame.event.get():
			#print event
			#quit when x button is pressed
			if event.type == pygame.QUIT: self.isRunning = False
			#check that the event has attr of key to prevent crashes
			if hasattr(event, 'key'):
				keys = pygame.key.get_pressed()
				if self.status["mapping"]:
					if keys[self.leftKey] and keys[self.shiftKey]:
						if self.currentBeat != "1:1:1":
							self.currentBeat = self.backwardSubBeat()
							self.loadMap()
					elif keys[self.leftKey]:
						if self.currentBeat != "1:1:1":
							for i in xrange(4):
								self.currentBeat = self.backwardSubBeat()
							self.loadMap()
					if keys[self.rightKey] and keys[self.shiftKey]:
						self.currentBeat = self.forwardSubBeat()
						self.loadMap()
					elif keys[self.rightKey]:
						for i in xrange(4):
							self.currentBeat = self.forwardSubBeat()
						self.loadMap()
				if keys[self.pKey]:
					if self.status["mapping"]:
						self.timerStart = time.time()
						self.timerDelay = convertTime(self.currentBeat, self.tempo)
						self.playMusic(self.music, self.timerDelay)
					if self.status["playback"]:
						self.timer = 0
						pygame.mixer.music.stop()
					self.status["mapping"] = not self.status["mapping"]
					self.status["playback"] = not self.status["playback"]
				if keys[self.eKey]:

					fout = open("parsed.txt","wt")
					beats = list()
					with open("beatmap.txt","rt") as fin:
						content = fin.read().split("\n")
						content.sort()
						times = list()
						print content
						for i in xrange(len(content)):
							if i <= 1 or i == len(content)-1: continue
							line = content[i]
							beats.append(line)
							end = string.find(line, "\"", 3)
							timeCurrent = line[2:end]
							currentTime = convertTime(timeCurrent,self.tempo)
							times.append(currentTime)
					times.sort()
					diffs = list()
					print times
					for i in xrange(len(times)):
						timer = times[i]
						diff = 0
						for j in xrange(2,len(times)):
							temp = times[i-j]
							if times != temp:
								diff = timer-temp
								break
						diffs.append(diff)
					lastMeasure = 0
					for beat in beats:
						end = string.find(beat, ":",2)
						temp = beat[2:end]
						if temp != "":
						 lastMeasure = int(temp) if int(temp)>int(lastMeasure) else lastMeasure
					print lastMeasure
					self.currentBeat = "1:1:1"
					pauseCount = 2
					for i in xrange(lastMeasure*16):
						print self.currentBeat
						if self.currentBeat in self.notes:
							times = self.notes[self.currentBeat]
							print times
							for pos in times:
								fout.write("overload.makeBlook("+str(pos[0])+","+str(pos[1])+");\n")
							fout.write("yield return new WaitForSeconds("+str(diffs[pauseCount])+"f);\n")
							pauseCount+=1
						self.currentBeat = self.forwardSubBeat()
					fout.close()

							#"yield return new WaitForSeconds(0.0f);"

							#makeBlock(x, y);





			if event.type == pygame.MOUSEBUTTONDOWN:
				(x,y)=pygame.mouse.get_pos()
				row,col = -1,-1
				if (x>=20 and x<=620 and
					y>=20 and y<=420):
					x-=20;
					y-=20;
					row = y/100
					col = x/100
					if self.currentBeatGrid[row][col] == 0:
						print "WRITING", row,col
						self.currentBeatGrid[row][col] = 1
						self.notes[self.currentBeat] = (col,row)
						self.writeMap(self.currentBeat,(col,row))
					else:
						print "REMOVING"
						self.currentBeatGrid[row][col] = 0
						vals = self.notes[self.currentBeat]
						vals.pop(vals.index((col,row)))
						self.notes[self.currentBeat] = vals
						self.removeMap(self.currentBeat,(col,row))

	def backwardSubBeat(self):
		beat = self.currentBeat.split(":")
		for i in xrange(len(beat)):
			beat[i] = int(beat[i])
		if beat[2]-1 != 0:
			beat[2]-=1
		else:
			beat[2]=4
			if beat[1]-1 != 0:
				beat[1]-=1
			else:
				beat[1] = 4
				beat[0] -=1
		beatText = str(beat[0])+":"+str(beat[1])+":"+str(beat[2])
		return beatText

	def forwardSubBeat(self):
		beat = self.currentBeat.split(":")
		for i in xrange(len(beat)):
			beat[i] = int(beat[i])
		if beat[2]+1 == 5:
			beat[2] = 1
			if beat[1]+1 == 5:
				beat[1] = 1
				beat[0]+=1
			else:
				beat[1] += 1
		else:
			beat[2] += 1
		beatText = str(beat[0])+":"+str(beat[1])+":"+str(beat[2])
		return beatText


		###############
		### MAKE UPDATE SELF.CURRENTBEAT ON BEAT CHANGE AND MODIFY BEATMAP.TXT UPON NOTE ENABLE/DISABLE
		###############b




	def menuUpdate(self, key):
		pass

	def resetMenuButtons(self):
		pass

	def instructionsUpdate(self, key):
		pass

	def optionsUpdate(self, key):
		pass

	def resetOptionButtons(self):
		pass

	def pausedUpdate(self, key):
		pass

	def gameOverUpdate(self, key):
		pass

	def gameWinUpdate(self, key):
		pass
	#I should change the weird default val thing... That's really hacky...
	def playingUpdate(self, key=None, keys=[0]*500):
		self.playerUIGroup.update()
		if self.status["playback"]:
			timer = time.time()-self.timerStart
			beats = self.currentBeat.split(":")
			for i in xrange(len(beats)):
				beats[i] = int(beats[i])
			checkTime = self.forwardSubBeat()
			if convertTime(checkTime,self.tempo)-self.timerDelay<timer:
				self.currentBeat = self.forwardSubBeat()
				self.loadMap()

			#self.currentBeat = 
		#################
		# EVENT HANDLER #
		#################
		if key != None:
			up = (key == "up") or keys[self.upKey]
			down = (key == "down") or keys[self.downKey]
			left = (key == "left") or keys[self.leftKey]
			right = (key == "right") or keys[self.rightKey]
			confirm = (key == "confirm")
			cancel = (key == "cancel")
			if down or up or left or right:
				print "asdf"
				self.sfx.cursorMove.play()
				if down: cursor.moveCursor((0,-1), self.currentLevel)
				if up: cursor.moveCursor((0,+1), self.currentLevel)
				if left: cursor.moveCursor((-1,0), self.currentLevel)
				if right: cursor.moveCursor((+1,0), self.currentLevel)
				tileType = self.currentLevel.map[cursor.truePos[1]][cursor.truePos[0]]
				self.gameInfoPanel3.update(tileType,self)
				for kanmusu in self.currentLevel.kanmusuDict:
					if (self.currentLevel.kanmusuDict[kanmusu].pos == cursor.truePos and
						self.currentLevel.selectedKanmusu == None):
						self.gameInfoPanel4.update(kanmusu, self)
						self.gameInfoPanel5.update(kanmusu, self)




	#########################
	###### GUI Drawing ######
	#########################

	def drawMenu(self):
		pass

	def playMusic(self, track,startTime=0):
		if pygame.mixer.music.get_busy():
			pygame.mixer.music.fadeout(1000) 
		pygame.mixer.music.load(track)
		pygame.mixer.music.set_volume(0.25)
		pygame.mixer.music.play(-1, startTime)

	def drawPlaying(self):
		#if not pygame.mixer.music.get_busy():
		#	print "a"
		#	pygame.mixer.music.load(self.music)
		#	pygame.mixer.music.set_volume(0)
		#	pygame.mixer.music.play(-1)

		self.drawGrid()
		for sprite in self.playerUIGroup:
			if isinstance(sprite, sprites.Cursor):
				blit_alpha(self.win,sprite.white, sprite.rect, sprite.alpha)
			self.win.blit(sprite.image,sprite.rect)

	def drawEditor(self):
		sideL = 100#px
		for row in xrange(len(self.currentBeatGrid)):
			for col in xrange(len(self.currentBeatGrid[row])):
				if self.currentBeatGrid[row][col] == 1:
					self.win.blit(self.approachBox,(self.left+col*sideL,self.top+row*sideL))
		self.drawGrid()
		self.drawInfo()

	def drawInfo(self):
		beatText = self.bigFont.render(self.currentBeat,True,(0,0,0))
		self.win.blit(beatText,(self.textX,self.textY+10))
		time = "%.2f" %convertTime(self.currentBeat,self.tempo)
		time +=" seconds"
		timeText = self.bigFont.render(time,True,(0,0,0))
		self.win.blit(timeText,(self.textX+400,self.textY+10))



	def drawGrid(self):
		sideL = 100#px
		#draw vert lines (cols)
		for i in xrange(7):
			pygame.draw.rect(self.win,(0,0,0),(self.left+i*sideL,self.top,0,self.height),2)
		#draw horizontal lines
		for i in xrange(5):
			pygame.draw.rect(self.win,(0,0,0),(self.left,self.top+i*sideL,self.length,0),2)

	def drawOptions(self):
		pass

	def drawInstructions(self):
		pass

	def redrawAll(self):
		self.win.fill((255,255,255))
		self.drawMenu()
		self.drawPlaying()
		self.drawEditor()
		pygame.display.update()
		


	def run(self):
		while self.isRunning == True:
			self.clock.tick(30)
			self.ticks += 1
			self.events()
			self.redrawAll()
		pygame.quit()

###############################
###### Main Run Function ######
###############################

def run():
	#Grab some vals from the config
	pygame.mixer.pre_init(44100, -16, 2, 2048)
	pygame.mixer.init()
	pygame.mixer.set_num_channels(32)
	pygame.init()
	pygame.display.set_caption("Thing")
	#pygame.display.set_icon(pygame.image.load(os.path.join(os.path.curdir,"img","gui","icon.png")))
	pygame.mouse.set_visible(1)
	pygame.event.set_allowed(None)
	pygame.event.set_allowed([pygame.QUIT,pygame.KEYDOWN,pygame.KEYUP,pygame.MOUSEBUTTONDOWN])
	win = pygame.display.set_mode((640,480))
	game = BeatmapVisualizer(win)
	game.run()
	#except:
	#	popup.error("Fatal Error", "Yikes! A fatal error just occurred!\nFear not though, I'll just restart the program.\nBasically, pygame sucks.")
	#	run()
#########################
##### Helper Funcs ######
#########################

#Give a measure:beat:subbeat string with a tempo and return time in m:s:ms
def convertTime(time,tempo):
	measure = 240.000/tempo
	beat = 60.000/tempo
	subbeat = 60.000/4/tempo
	time = time.split(":")
	for i in xrange(len(time)):
		time[i] = int(time[i])
	total = (time[0]-1)*measure+(time[1]-1)*beat+(time[2]-1)*subbeat
	return total



#pos1 and pos2 should both be a list or tuple with two indexes, an x and y.
def getDisplacement(pos1,pos2):
	dy = pos1[1]-pos2[1]
	dx = pos1[0]-pos2[0]
	displacement = abs(dy)+abs(dx)
	return displacement

#pos1 is start, pos2 is destination
def getRecursiveCheapestPath(pos1,pos2):
	pass

def remakeConfig():
	config = dict()
	popup.error("Incorrect Config", "No config file exists or is broken! Creating new one!")
	fout = open("config.txt", "wt")
	fout.write(defaultVals.config())
	fout.close()
	return parseConfigVals(defaultVals.config().split("\n"))

def parseConfigVals(config):
	#Incase for whatever reason the provided config data
	#hasn't yet been split into lines yet.
	if type(config) != list:
		config = config.split("\n")
	listOfVals = dict()
	#add the vals to a dict with the key 
	for line in config:
		index = line.find(":")
		if index != -1:
			val = line[index+1:].strip(string.whitespace)
			key = line[0:index].strip(string.whitespace)
			listOfVals[key] = val
	return listOfVals

def modifyConfigVals(key, val):
	fin = fout = None
	try:
		fin = open("config.txt", "rt")
		fout = open("temp.txt","wt")
		content = fin.read()
		start = string.find(content, key)+len(key)+1
		end = string.find(content, "\n", start)
		part1 = content[:start]
		part2 = " "+str(val)
		part3 = content[end:]
		fout.write(part1+part2+part3)

	except:
		config = remakeConfig()
	finally:
		if fin != None: fin.close()
		if fout != None: fout.close()
		os.remove("config.txt")
		os.rename("temp.txt","config.txt")

# http://www.nerdparadise.com/tech/python/pygame/blitopacity/
# Alpha blitting for per-pixel alpha surfaces	
def blit_alpha(target, source, location, opacity, area=None):
	x = location[0]
	y = location[1]
	temp = pygame.Surface((source.get_width(), source.get_height())).convert()
	temp.blit(target, (-x, -y))
	temp.blit(source, (0, 0))
	temp.set_alpha(opacity)
	if area == None: target.blit(temp, location)
	else: target.blit(temp, location, area)







####################
# THE ALL HOLY RUN #
####################
####################
run() ##############
####################
####################

#  .----.-----.-----.-----.
# /      \     \     \     \
#|  \/    |     |   __L_____L__
#|   |    |     |  (           \
#|    \___/    /    \______/    |
#|        \___/\___/\___/       |
# \      \     /               /
#  |                        __/
#   \_                   __/
#    |        |         |
#    |                  |
#    |                  |


























