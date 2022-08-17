# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 23:39:14 2020

@author: Cyrano
"""

#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np
import sys
import os
from skimage.filters import rank
import qimage2ndarray
import spotipy
import spotipy.util as util
from json.decoder import JSONDecodeError
import playsound
import threading

#Other classes
from tile import Tile


class EncounterGrid(QtWidgets.QWidget):
    
    def __init__(self):
        super().__init__()
        
        
        #game_variables
        self.w              = 16
        self.h              = 9
        self.hp             = 100
        self.maxHp          = self.hp
        # self.time           = 60
        # self.maxTime        = self.time
        self.delta          = None
        self.encounter      = 0
        self.turn           = 0
        self.actions        = []
        self.gameOverQ      = False
        self.songs          = []
        self.hpThresh       = 0
        self.hpThreshActive = False
        self.hpThreshFlag   = False
        
        #init stuff
        self.initGui()
        self.initSpotipy()
        
        # self.timer = QtCore.QTimer()
        # self.timer.timeout.connect(self.updateTime)
        
    def initGui(self):
        
        self.box_layout = QtWidgets.QGridLayout()
        self.box_layout.setSpacing(0);
        self.box_layout.setContentsMargins(0, 0, 0, 0);
        
        
        self.hpBar  = QtWidgets.QProgressBar()
        self.hpBar.setValue(self.hp)
        self.hpBar.setMaximum(self.hp)
        self.hpBar.setFormat("") 
        self.hpBar.setStyleSheet("QProgressBar"
                                 "{"
                                 "background-color : black;"
                                 "border : 1px;"
                                 "color : red;"
                                 "text-align: center"
                                 "}"
                                 
                                 "QProgressBar::chunk"
                                 "{"
                                 "background-color: red;"
                                 "}"
                                 ) 
        
        self.layout     = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(0);
        self.layout.setContentsMargins(0, 0, 0, 0);
        self.layout.addWidget(self.hpBar)
        self.layout.addLayout(self.box_layout)
        
        
        self.horLayout  = QtWidgets.QHBoxLayout()
        # self.horLayout.addWidget(self.timeBar)
        self.horLayout.addLayout(self.layout)
        self.horLayout.setSpacing(0);
        self.horLayout.setContentsMargins(0, 0, 0, 0);
        
        self.setLayout(self.horLayout)
        
        self.setGeometry(300, 300, 300, 300)
        self.loadAssets()
        self.set_board_state()
        self.showFullScreen()
        self.show()
        
        
    def loadAssets(self):
        self.assetDir = os.path.join(os.getcwd(), "Assets")    
        
        #go over all assets, load them into memory
    

    #%%Signals and slots
        
    def pressedSlot(self, x,y, asset):
        
            if self.gameOverQ:
                return
        
            #Checks which asset is pressed and which rule is asociated with 
            #that tile. 
        
    
       #%% board state
           
           
    def set_board_state(self):  
        #Fills the board with empty tiles
        
        positions = [(i,j) for i in range(self.h) for j in range(self.w)]
        
        for position in positions:
            box = Tile(position[0], position[1])
            box.pressedSignal.connect(self.pressedSlot)
            self.box_layout.addWidget(box, *position)
            
            
    def reset_board_state(self):
        #Resets all tile statuses, reloads the current encounter
        
        self.gameOverQ = False
        for x in range(0,self.w):
            for y in range(0, self.h):
                self.box_layout.itemAtPosition(
                    y,x).widget().setProtected(False)
                self.box_layout.itemAtPosition(y,x).widget().asset = None
                self.box_layout.itemAtPosition(y,x).widget().resetTile()
        self.turn = 0
        self.clearSongs()
        self.newTurn()
        
        
    def empty_board_state(self):
        #Ends the encounter and clears all tiles
        
        self.gameOverQ = True
        for x in range(0,self.w):
            for y in range(0, self.h):
                self.box_layout.itemAtPosition(
                    y,x).widget().setProtected(False)
                self.box_layout.itemAtPosition(y,x).widget().asset = None
                self.box_layout.itemAtPosition(y,x).widget().resetTile()
                self.resetTime()
           
           
    def resetForNextTurn(self):
        for x in range(0,self.w):
            for y in range(0, self.h):
                #first check for crystals
                if self.box_layout.itemAtPosition(y,x).widget().getProtected():
                    continue
                
                self.box_layout.itemAtPosition(y,x).widget().resetTile()
        
        
    #%% game state
        
    def gameOver(self):
        
        self.gameOverQ = True
        self.hpBar.setValue(0)
        
        for i in range(0,self.w):
            for j in range(0, self.h):
                self.box_layout.itemAtPosition(
                    j,i).widget().setProtected(False)
                self.box_layout.itemAtPosition(j,i).widget().asset = None
                self.box_layout.itemAtPosition(j,i).widget().resetTile()
                self.box_layout.itemAtPosition(j,i).widget().loadAsset(
                    "void_black.png", None)
                
    def nextTurn(self):
        self.turn += 1
        self.newTurn()
    
    def prevTurn(self):
        pass
    
    def newTurn(self):
        
        if self.gameOverQ:
            return
        
        if len(self.actions) == 0:
            return
        
        if not self.checkGameOver():
            return
        
        #Load all the actions as described by the encounter document. 
        #List of supported actions:
        #   - addSong       adds a song to the playlist
        #   - remove        clears a tile at position
        #   - hp            sets boss hp
        #   - hpThresh      sets hp threshold 
        #   - gameOver      clears the board
        #   - playSongs     starts playing the songs in playlist
        #   - clearSongs    stops playing and removes all songs 
        #   - timer         sets (and starts) a timer
        #   
        #   - if the action specified is a usable filename, the asset at that
        #       location is loaded and displayed at x,y
        
        todo    = []
        for action in self.actions:
            if action[0] == self.turn:
                todo.append(action)
                
        for action in todo:
            x = action[1]
            y = action[2]
            asset = action[3]
            
            if asset == "addSong":
                self.addSongToList(x)
                continue
            
            x = int(x)            
            
            if asset == "remove":
                self.box_layout.itemAtPosition(
                    y,x).widget().setProtected(False)
                self.box_layout.itemAtPosition(y,x).widget().asset = None
                self.box_layout.itemAtPosition(y,x).widget().resetTile()
            if asset == "hp":
                if x == 0:
                    self.hpBar.setValue(0)   
                else:
                    self.hp = x
                    self.maxHp = x
                    self.hpBar.setMaximum(self.hp)
                    self.hpBar.setValue(self.hp)   
            elif asset == "hpThresh":
                self.hpThresh = x
                self.hpThreshActive = True
            elif asset == "gameOver":
                self.gameOver()
                    
            elif asset == "empty":
                self.empty_board_state()
            elif asset == "playSongs":
                self.playSongs()
            elif asset == "clearSongs":
                self.clearSongs()
            elif asset == "timer":
                self.timer.stop()
                self.maxTime = x
                self.time = x
                self.startTimer()
            else:
                self.box_layout.itemAtPosition(y,x).widget().setProtected(True)
                self.box_layout.itemAtPosition(y,x).widget().loadAsset(
                    asset, None)
                
    #%% user input
        
    def keyPressEvent(self, event):
        super(EncounterGrid, self).keyPressEvent(event)
        
        key = event.key()
        #Turns
        if key == QtCore.Qt.Key_Q:
            self.nextTurn()
        elif key == QtCore.Qt.Key_P:
            self.reset_board_state()
        elif key == QtCore.Qt.Key_E:
            self.empty_board_state()
            
            
        elif key == QtCore.Qt.Key_L:
            self.loadEncounter()
        elif key == QtCore.Qt.Key_G:
            self.gameOver()
            
        #This is used to manipulate values (like boss hp)           
        elif key == QtCore.Qt.Key_Minus:
            self.startValue(-1)
        elif key == QtCore.Qt.Key_Equal:
            self.startValue(1)
        elif key == QtCore.Qt.Key_Plus:
            self.startValue(1)
        elif key == QtCore.Qt.Key_Enter:
            self.addValue()
        elif key == QtCore.Qt.Key_Return:
            self.addValue()
        elif key == QtCore.Qt.Key_0:
            self.changeValue(0)
        elif key == QtCore.Qt.Key_1:
            self.changeValue(1)
        elif key == QtCore.Qt.Key_2:
            self.changeValue(2)
        elif key == QtCore.Qt.Key_3:
            self.changeValue(3)
        elif key == QtCore.Qt.Key_4:
            self.changeValue(4)
        elif key == QtCore.Qt.Key_5:
            self.changeValue(5)
        elif key == QtCore.Qt.Key_6:
            self.changeValue(6)
        elif key == QtCore.Qt.Key_7:
            self.changeValue(7)
        elif key == QtCore.Qt.Key_8:
            self.changeValue(8)
        elif key == QtCore.Qt.Key_9:
            self.changeValue(9)
         
        else:
            return    
        
    def loadEncounter(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self,
                                                      'Load new encounter',
                                                      '',
                                                      '(*.txt)')
        if len(fname[0]) == 0:
            return
        
        self.encounter = int(fname[0][-5])
        
        with open(fname[0]) as f:
            lines = f.readlines()
        
        self.actions = []
        for line in lines:
            parts = line.split()
            turn    = int(parts[0])
            x       = str(parts[1])
            y       = int(parts[2])
            asset   = parts[3]
            
            self.actions.append([turn,x,y,asset])
        
        self.reset_board_state()
        
        

    #%% hp stuff

    def startValue(self, plusminus):
        self.delta  = 0
        self.plusminus    = plusminus
        
    def changeValue(self, val):
        if self.delta == None:
            return
        
        self.delta  = int(str(self.delta) + str(val))
    
    def addValue(self):
        if self.delta == None:
            return
        
        self.hp     += self.delta * self.plusminus
        self.hp     = min(max(0, self.hp), self.maxHp)
        self.delta  = None
        
        if self.hp <= self.hpThresh and self.hpThreshActive:
            self.hp = self.hpThresh
            self.changeHPColor()
            self.hpThreshActive = False
            self.hpThreshFlag   = True
        
        self.hpBar.setValue(self.hp)   

    def changeHPColor(self):
        
        if self.hpThreshActive:
            self.hpBar.setStyleSheet("QProgressBar"
                                 "{"
                                 "background-color : black;"
                                 "border : 1px;"
                                 "color : red;"
                                 "text-align: center"
                                 "}"
                                 
                                 "QProgressBar::chunk"
                                 "{"
                                 "background-color: orange;"
                                 "}"
                                 ) 
        else:
            self.hpBar.setStyleSheet("QProgressBar"
                                 "{"
                                 "background-color : black;"
                                 "border : 1px;"
                                 "color : red;"
                                 "text-align: center"
                                 "}"
                                 
                                 "QProgressBar::chunk"
                                 "{"
                                 "background-color: red;"
                                 "}"
                                 ) 

        
    #%% timer stuff
        
    # def startTimer(self):
    #     self.time = self.maxTime
    #     self.timeBar.setValue(self.time)
    #     self.timeBar.setFormat(str(self.time))
    #     self.timer.start(1000)
        
    
    # def updateTime(self):
    #     self.time -= 1
    #     self.timeBar.setValue(self.time)
    #     self.timeBar.setFormat(str(self.time))
        
    #     if self.time <= 0:
    #         self.timeUp()
    
    # def timeUp(self):
    #     self.timer.stop()
        
    # def resetTime(self):
    #     self.timeUp()
    #     self.time = self.maxTime
    #     self.timeBar.setValue(self.time)
    #     self.timeBar.setFormat(str(self.time))
        
        
    #%% song stuff
    
    def initSpotipy(self):
        username = 'crnchtzntn@gmail.com'
        scope = \
    'user-read-private user-read-playback-state user-modify-playback-state'
        
        os.environ['SPOTIPY_CLIENT_ID'] = ''
        os.environ['SPOTIPY_CLIENT_SECRET'] = ''
        os.environ['SPOTIPY_REDIRECT_URI'] = 'https://www.google.nl/'
        
        try:
            token = util.prompt_for_user_token(username, scope)
        except (AttributeError, JSONDecodeError):
            os.remove(f".cache-{username}")
            token = util.prompt_for_user_token(username, scope)
            
        self.spotifyObject = spotipy.Spotify(auth=token)

        devices     = self.spotifyObject.devices()
        self.deviceID    = -1
        for i in range(len(devices)):
            if devices['devices'][i]['name'] == "TI-85":
                self.deviceID    = devices['devices'][i]['id']
        
        if self.deviceID == -1:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Correct spotify device not found.')
            return
    
    def addSongToList(self, songID):
        songKey     = "spotify:track:" + songID
        self.songs.append(songKey)
        
    def playSongs(self):
        #voodoo magic spotipy api
        # return
        if self.deviceID == -1:
            return
        
        self.spotifyObject.start_playback(
            self.deviceID, None, self.songs)
        
    def clearSongs(self):
        self.songs  = []
        
        
            
if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)
    eg  = EncounterGrid()
    sys.exit(app.exec_())
