#!/usr/bin/env python

# neaten

from random import randint
import Tkinter as tK
import time

# TK Constants
BG_COLOR = "#36594A"
FG_COLOR = "#FFFFFF"
BOARD_SIZE = "1200x1500"
CARD_WIDTH = 108
CARD_HEIGHT = 150
BOARD_WIDTH = 1200
BOARD_HEIGHT = 1000

def valueToString(v):
	if v == 1:
		v = "A"
	elif v == 11:
		v = "J"
	elif v == 12:
		v = "Q"
	elif v == 13:
		v = "K"
	else:
		v = str(v)
	return v

def timeConvert(seconds):
	minutes = seconds // 60
	seconds %= 60
	return "%02d:%02d" % (minutes, seconds)

class card:
	def __init__(self, cardValue, cardSuit, cardLocation, game):
		self.value = cardValue
		self.suit = cardSuit
		if (self.suit == "Hearts") or (self.suit == "Diamonds"):
			self.color = "Red"
			self.text_color = "#FF0000"
		else:
			self.color = "Black"
			self.text_color = "#1B1E23"
		self.movable = False
		self.show = False
		self.x = 0
		self.y = 0
		self.game = game
		self.play = self.game.playPiles
		self.win = self.game.winPiles
		self.canvas = self.game.playFrame
		self.pile = cardLocation
		self.cardImgFile = '.\\card_images\\%s%s.gif' % (valueToString(self.value), self.suit)
		self.faceImg = tK.PhotoImage(file=self.cardImgFile)
		self.backImg = tK.PhotoImage(file='.\\card_images\\cardback.gif')
		self.face = tK.Label(self.canvas, image=self.faceImg, borderwidth=4, relief="raised", bg="#FFFFFF", width=CARD_WIDTH, height=CARD_HEIGHT)
		self.back = tK.Label(self.canvas, image=self.backImg, borderwidth=4, relief="raised", width=CARD_WIDTH, height=CARD_HEIGHT)
		self.face.bind("<Button-1>", self.drag_start)
		self.face.bind("<B1-Motion>", self.drag_motion)
		self.face.bind("<ButtonRelease-1>", self.placeOrSnap)

	def flipFaceUp(self, x, y):
		self.x = x
		self.y = y
		self.face.place(x=x, y=y, height=CARD_HEIGHT, width=CARD_WIDTH)
		self.face.lift()
		self.back.place_forget()
		self.show = True

	def flipFaceDown(self, x, y):
		self.x = x
		self.y = y
		self.back.place(x=x, y=y, height=CARD_HEIGHT, width=CARD_WIDTH)
		self.back.lift()
		self.face.place_forget()
		self.show = False

	def drag_start(self, event):
		if self.movable:
			for i in range(self.pile.findCard(self), len(self.pile.stack)):
				cardInStack = self.pile.stack[i]
				cardInStack.face.startX = cardInStack.x
				cardInStack.face.startY = cardInStack.y
				cardInStack.face.dragStartX = event.x
				cardInStack.face.dragStartY = event.y

	def drag_motion(self, event):
		if self.movable:
			for i in range(self.pile.findCard(self), (len(self.pile.stack))):
				cardInStack = self.pile.stack[i]
				cx = cardInStack.face.winfo_x() - cardInStack.face.dragStartX + event.x
				cy = cardInStack.face.winfo_y() - cardInStack.face.dragStartY + event.y
				cardInStack.face.place(x=cx, y=cy)
				cardInStack.face.lift()
				cardInStack.x = cx
				cardInStack.y = cy

	def placeOrSnap(self, event):
		if self.movable:
			for winPileIndex in range(0, 4):
				if (self.x + event.x >= self.win[winPileIndex].x) and (
						self.x + event.x <= self.win[winPileIndex].x + self.win[winPileIndex].width) and (
						self.y + event.y >= self.win[winPileIndex].y) and (
						self.y + event.y <= self.win[winPileIndex].y + self.win[winPileIndex].height):
					if self.pile.findCard(self) == (len(self.pile.stack) - 1) and (
							(self.win[winPileIndex].canPlay(self)) == 1):
						self.pile.pop(len(self.pile.stack)-1)
						self.pile = self.win[winPileIndex]
						self.face.place(x=self.win[winPileIndex].x + 7, y=self.win[winPileIndex].y + 7)
						self.x = self.win[winPileIndex].x + 7
						self.y = self.win[winPileIndex].y + 7
						self.face.lift()
					self.game.winCheck()
					return
			for playPileIndex in range(0, 7):
				if (self.x + event.x >= self.play[playPileIndex].x) and (
						self.x + event.x <= self.play[playPileIndex].x + self.play[playPileIndex].width) and (
						self.y + event.y >= self.play[playPileIndex].y) and (
						self.y + event.y <= self.play[playPileIndex].y + self.play[playPileIndex].height) and self.play[
					playPileIndex].canPlay(self):
					cardsInStack = len(self.pile.stack) - self.pile.findCard(self)
					heldCardPos = self.pile.findCard(self)
					oldPile = self.pile
					for stackIndex in reversed(range(heldCardPos, heldCardPos+cardsInStack)):
						cardInStack = oldPile.stack[heldCardPos]
						cardInStack.pile = self.play[playPileIndex]
						self.play[playPileIndex].stack.append(oldPile.pop(heldCardPos))
						self.play[playPileIndex].y += 33
						cardInStack.face.place(x=self.play[playPileIndex].x, y=self.play[playPileIndex].y)
						cardInStack.x = self.play[playPileIndex].x
						cardInStack.y = self.play[playPileIndex].y
						cardInStack.face.lift()
					return

			for playPileIndex in range(self.pile.findCard(self), (len(self.pile.stack))):
				cardInStack = self.pile.stack[playPileIndex]
				cardInStack.face.place(x=cardInStack.face.startX, y=cardInStack.face.startY)
				cardInStack.x = cardInStack.face.startX
				cardInStack.y = cardInStack.face.startY

class deck:
	def __init__(self, game):
		self.stack = []
		self.game = game
		self.buildDeck()
		self.shuffleDeck()
		self.displayDeck()

	def buildDeck(self):
		for s in ["Hearts", "Diamonds", "Clubs", "Spades"]:
			for v in range(1, 14):
				self.stack.append(card(v, s, self, self.game))

	def debugShowDeck(self):
		for c in self.stack:
			print(c.text)

	def shuffleDeck(self):
		tempDeck = []
		for i in range(52, 0, -1):
			tempDeck.append(self.stack.pop((randint(1, i) - 1)))
		self.stack = tempDeck

	def displayDeck(self):
		for i in range(0, 52):
			cardInDeck = self.stack[i]
			cardInDeck.flipFaceDown(10, 50)

	def findCard(self, card):
		for i in range(len(self.stack)):
			if self.stack[i] == card:
				return i

	def pop(self):
		return self.stack.pop()

	def push(self, item):
		return self.stack.append(item)


class winPile:
	def __init__(self, pileSuit, x, y, canvas):
		self.x = x
		self.y = y
		self.width = CARD_WIDTH + 10
		self.height = CARD_HEIGHT + 10
		self.stack = []
		self.suit = pileSuit
		self.canvas = canvas
		self.win = tK.Canvas(canvas, width=self.width, height=self.height, bg="#808080", bd=1)
		self.win_label = tK.Label(canvas, text=self.suit, bg=BG_COLOR, fg=FG_COLOR, font=("Comic Sans MS", 12))
		self.win.place(x=self.x, y=self.y)
		self.win_label.place(x=self.x, y=self.y + CARD_HEIGHT + 15)

	def canPlay(self, item):
		if self.isEmpty():
			if (item.suit == self.suit) and (item.value == 1):
				self.stack.append(item)
				return 1
			else:
				return 0
		else:
			topCard = self.peak()
			if (item.suit == self.suit) and (item.value == (topCard.value + 1)):
				self.stack.append(item)
				return 1
			else:
				return 0

	def findCard(self, card):
		for i in range(len(self.stack)):
			if (self.stack[i] == card):
				return i

	def pop(self, index):
		return self.stack.pop(index)

	def peak(self):
		return self.stack[len(self.stack) - 1]

	def isEmpty(self):
		return self.stack == []

class standbyPile:
	def __init__(self):
		self.stack = []
		self.x = 10
		self.y = 210

	def draw3(self, deck):
		if (self.isEmpty() == False):
			self.stack[len(self.stack) - 1].movable = False
		if (len(deck.stack) < 3):
			cardsDrawn = len(deck.stack)
		else:
			cardsDrawn = 3
		cardsInPile = len(self.stack)
		for i in range(cardsDrawn):
			self.stack.append(deck.pop())
			self.stack[cardsInPile + i].pile = self
			self.stack[cardsInPile + i].flipFaceUp(self.x, self.y + (33 * i))
		self.stack[len(self.stack) - 1].movable = True

	def refillDeck(self, deck):
		for i in range(len(self.stack)):
			card = self.pop(len(self.stack)-1)
			card.pile = deck
			card.flipFaceDown(10, 50)
			deck.push(card)

	def findCard(self, card):
		for i in range(len(self.stack)):
			if self.stack[i] == card:
				return i

	def pop(self, index):
		if (len(self.stack) > 1):
			self.stack[len(self.stack) - 2].movable = True
		return self.stack.pop(index)

	def isEmpty(self):
		return self.stack == []

class playPile:
	def __init__(self, initCards, x, y, cardSource):
		self.x = x
		self.y = y
		self.height = CARD_HEIGHT
		self.width = CARD_WIDTH
		self.stack = []
		self.startNum = initCards
		self.buildPile(cardSource)

	def buildPile(self, deck):
		for i in range(self.startNum):
			self.stack.append(deck.pop())
			self.stack[i].pile = self
			self.stack[i].flipFaceDown(self.x, self.y + (33 * i))
			if i == (self.startNum - 1):
				self.stack[i].flipFaceUp(self.x, self.y + (33 * i))
				self.stack[i].movable = True
				self.y = (self.y + (33 * (i)))

	def pop(self, index):
		self.y = (self.y - 33)
		card = self.stack[len(self.stack) - 2]
		if card.show == False:
			card.flipFaceUp(self.x, self.y)
			card.movable = True
		return self.stack.pop(index)

	def findCard(self, card):
		for i in range(len(self.stack)):
			if self.stack[i] == card:
				return i

	def canPlay(self, item):
		if len(self.stack) == 0:
			if item.value == 13:
				return 1
			else:
				return 0
		else:
			stackCard = self.stack[len(self.stack) - 1]
			if stackCard.value == 1:
				return 0
			if (item.color != stackCard.color) and (item.value == (stackCard.value - 1)):
				return 1
			else:
				return 0

class Solitaire:
	def __init__(self, master):
		self.master = master
		self.master.wm_title("Solitaire")
		self.master.geometry(BOARD_SIZE)
		self.winPiles = []
		self.playPiles = []
		self.hsName = []
		self.hsTime = []
		self.hsLabels = []
		self.playFrame = tK.Frame(self.master, bg=BG_COLOR, height=BOARD_HEIGHT, width=BOARD_WIDTH)
		self.highScoreFrame = tK.Frame(self.master, bg=BG_COLOR, height=BOARD_HEIGHT, width=BOARD_WIDTH)
		self.winFrame = tK.Frame(self.master, bg=BG_COLOR, height=BOARD_HEIGHT, width=BOARD_WIDTH)
		self.initGame()
		self.timeToComplete=0

		# Play Frame
		self.playFrame.pack_propagate(0)
		self.playTimer = tK.Label(self.playFrame, bg=BG_COLOR, text="00:00", fg=FG_COLOR, font=("Comic Sans MS", 36))
		self.dealButton = tK.Button(self.playFrame,text="Deal",command=lambda: self.deal(self.standby))
		self.resetButton = tK.Button(self.playFrame, text="Reset", command=self.reset)
		self.highscoreButton = tK.Button(self.playFrame, text="HighScore", command=lambda: self.frameSwitch(self.highScoreFrame, self.playFrame))
		self.quitButton = tK.Button(self.playFrame, text="Quit", command=self.master.destroy)

		# HighScore Frame
		self.hsReadIn()
		self.highScoreFrame.pack_propagate(0)
		self.hsTitle = tK.Label(self.highScoreFrame, text="HIGHSCORE", bg=BG_COLOR, fg=FG_COLOR, font=("Comic Sans MS", 24))
		for hs in range(0, 5):
			hsText = str(hs+1) + ") " + self.hsName[hs] + " - " + timeConvert(int(self.hsTime[hs]))
			self.hsLabels.append(tK.Label(self.highScoreFrame, bg=BG_COLOR, fg=FG_COLOR, text=hsText, font=("Comic Sans MS", 18)))
			self.hsLabels[hs].place(x=200, y=200 + (100 * hs), height=50, width=600)

		self.playButton = tK.Button(self.highScoreFrame, text="Play", command=lambda: self.frameSwitch(self.playFrame, self.highScoreFrame))
		self.hsQuitButton = tK.Button(self.highScoreFrame, text="Quit", command=self.master.destroy)

		# Win Frame
		self.winFrame.pack_propagate(0)
		self.winBanner = tK.Canvas(self.winFrame, bd=10, relief="raised", bg="#0000FF", width=800, height=500)
		self.winBanner.create_text(375, 150, text="YOU WIN!", fill="#FFD700", font=("Comic Sans MS", 72))
		self.winEntry = tK.Entry(self.winFrame, bd=5, font=("Comic Sans MS", 18))
		self.submitButton = tK.Button(self.winFrame, text="Submit", command=lambda: self.hsUpdate())
		self.newGameButton = tK.Button(self.winFrame, text="New Game", command=lambda: self.frameSwitch(self.playFrame, self.winFrame))

		# Play Pack
		self.dealButton.place(x=200, y=0, height=50, width=100)
		self.resetButton.place(x=300, y=0, height=50, width=100)
		self.highscoreButton.place(x=400, y=0, height=50, width=100)
		self.quitButton.place(x=500, y=0, height=50, width=100)
		self.playTimer.place(x=300, y=125, height=50, width=200)

		# HS Pack
		self.hsTitle.place(x=400, y=120, height=50, width=200)
		self.playButton.place(x=400, y=0, height=50, width=100)
		self.hsQuitButton.place(x=500, y=0, height=50, width=100)

		# Win Pack
		self.winBanner.place(x=200, y=100, height=500, width=800)

		# Play Frame Pack Start Loop
		self.playFrame.pack()
		self.updateClock()

	def hsReadIn(self):
		f = open("hs_data", "r")
		for line in f:
			line = line.strip("\n")
			hsData = line.split(":")
			self.hsName.append(hsData[0])
			self.hsTime.append(hsData[1])

	def hsWriteOut(self):
		f = open("hs_data", "w")
		for hs in range(0, 5):
			hsData = self.hsName[hs] + ":" + str(self.hsTime[hs])
			f.write(hsData)
			if hs!=4:
				f.write("\n")


	def deal(self, pile):
		if len(self.mainPile.stack) == 0:
			pile.refillDeck(self.mainPile)
		else:
			pile.draw3(self.mainPile)

	def reset(self):
		self.destroyGame()
		self.initGame()

	def updateClock(self):
		now = timeConvert(int(round(time.time() - self.t0)))
		self.playTimer.configure(text=now)
		self.master.after(1000, self.updateClock)

	def frameSwitch(self, risingFrame, fallingFrame):
		fallingFrame.pack_forget()
		risingFrame.pack()

	def destroyGame(self):
		for i in reversed(range(len(self.mainPile.stack))):
			self.mainPile.stack[i].face.destroy()
			self.mainPile.stack[i].back.destroy()
			del self.mainPile.stack[i]
		del self.mainPile
		for i in reversed(range(0, 4)):
			for j in reversed(range(len(self.winPiles[i].stack))):
				self.winPiles[i].stack[j].face.destroy()
				self.winPiles[i].stack[j].back.destroy()
				del self.winPiles[i].stack[j]
			del self.winPiles[i]
		for i in reversed(range(len(self.standby.stack))):
			self.standby.stack[i].face.destroy()
			self.standby.stack[i].back.destroy()
			del self.standby.stack[i]
		del self.standby
		for i in reversed(range(0, 7)):
			for j in reversed(range(len(self.playPiles[i].stack))):
				self.playPiles[i].stack[j].face.destroy()
				self.playPiles[i].stack[j].back.destroy()
				del self.playPiles[i].stack[j]
			del self.playPiles[i]

	def initGame(self):
		self.mainPile = deck(self)
		for i in range(0, 4):
			if (i == 0):
				suit = "Hearts"
			elif (i == 1):
				suit = "Diamonds"
			elif (i == 2):
				suit = "Clubs"
			elif (i == 3):
				suit = "Spades"
			self.winPiles.append(winPile(suit, 630 + (120 * i), 10, self.playFrame))
		self.standby = standbyPile()
		for i in range(1, 8):
			self.playPiles.append(playPile(i, 90 + (110 * i), 220, self.mainPile))
		self.t0 = time.time()

	def winCheck(self):
		for i in range(0, 4):
			if len(self.winPiles[i].stack)!=13:
				return
			else:
				self.win()

	def win(self):
		self.t1 = time.time()
		self.timeToComplete = int(round(self.t1 - self.t0))
		self.hsCheck()
		self.frameSwitch(self.winFrame, self.playFrame)
		self.reset()

	def hsCheck(self):
		for hs in range(0, 5):
			if self.timeToComplete < self.hsTime[hs]:
				self.winBanner.create_text(375, 450, text="Time:" + timeConvert(self.timeToComplete), fill="#FFD700", font=("Comic Sans MS", 32))
				self.winEntry.place(x=525, y=400, height=50, width=200)
				self.submitButton.place(x=425, y=400, height=50, width=100)
			else:
				self.newGameButton.place(x=475, y=400, height=50, width=200)

	def hsUpdate(self):
		if self.winEntry.get() == "":
			return
		else:
			for hs in range(0, 5):
				if self.timeToComplete < self.hsTime[hs]:
					holdName = self.hsName[hs]
					holdTime = self.hsTime[hs]
					self.hsName[hs] = self.winEntry.get()
					self.hsTime[hs] = self.timeToComplete
					for i in range(hs+1, 5):
						temp = self.hsName[i]
						temp1 = self.hsTime[i]
						self.hsName[i] = holdName
						self.hsTime[i] = holdTime
						holdName = temp
						holdTime = temp1
						hsText = str(i + 1) + ") " + self.hsName[i] + " - " + timeConvert(int(self.hsTime[i]))
						self.hsLabels[i] = tK.Label(self.highScoreFrame, bg=BG_COLOR, fg=FG_COLOR, text=hsText,font=("Comic Sans MS", 18))
						self.hsLabels[i].place(x=200, y=200 + (100 * i), height=50, width=600)
					self.hsWriteOut()
					self.frameSwitch(self.highScoreFrame, self.winFrame)
					return


def main():
	root = tK.Tk()
	game = Solitaire(root)
	root.mainloop()

if __name__ == '__main__':
	main()