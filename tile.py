# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 19:13:22 2022

@author: Cyrano
"""
from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np
import os


class Tile(QtWidgets.QWidget):
    pressedSignal   = QtCore.pyqtSignal(int, int, str)
    
    def __init__(self, x, y):
        super().__init__()
        self.x          = x
        self.y          = y
        
        self.tileDir    = os.path.join(os.getcwd(), "Tiles")
        self.assetDir   = os.path.join(os.getcwd(), "Assets")
        tileLst         = os.listdir(self.tileDir)

        self.tileIdx    = np.random.randint(2,len(tileLst))
        self.angle      = np.random.randint(0,4) * 90
        
        
        #Game variables
        self.protected  = False
        self.plane      = 0
        self.asset      = None
        
        self.initGUI()
        
        
    def initGUI(self):
        
        
        self.scene  = QtWidgets.QGraphicsScene()
        self.view   = QtWidgets.QGraphicsView(self.scene)
        self.view.setStyleSheet("QGraphicsView"
                                 "{"
                                 "background-color : black;"
                                 "border : 1px;"
                                 "color : black;"
                                 "}"
                                 ) 
        
        #Load tile
        self.loadTile()
        self.scene.update()
        
        #Init gif label
        # self.lab     = QtWidgets.QLabel()
        
        self.layout     = QtWidgets.QHBoxLayout()
        self.layout.setSpacing(0);
        self.layout.setContentsMargins(0, 0, 0, 0);
        self.layout.addWidget(self.view)
        
        self.view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setLayout(self.layout)
        
    ###Public
        
    def setProtected(self, protected):
        self.protected = protected
        # self.resetTile()
    
    def getProtected(self):
        return self.protected
    
    def loadAsset(self, asset, gif):
        self.asset  = asset
        if gif is not None:
            self.loadGif(gif)
            return
        
        assetDir    = os.path.join(os.getcwd(), "Assets")
        pixmap = QtGui.QPixmap(os.path.join(assetDir, asset))
        self.scene.addPixmap(pixmap)
        
    ###Private
        
    #Events
    def mousePressEvent(self, e):
        self.pressed(e)
        
            
    #User input
    
    def pressed(self, event):
        
        self.pressedSignal.emit(self.x, self.y, self.asset)
        
    #Change Images
        
    def resetTile(self):
        items    = self.scene.items()
        for item in items:
            self.scene.removeItem(item)
        self.loadTile()   
        
    
    def loadTile(self):
        tileLst     = os.listdir(self.tileDir)
        
        pixmap = QtGui.QPixmap(
            os.path.join(self.tileDir, tileLst[self.tileIdx]))
        
        #rotate random direction
        rotate  = QtGui.QTransform()
        rotate.rotate(self.angle)
        pixmap  = pixmap.transformed(rotate)
        
        self.scene.addPixmap(pixmap)        
        
    def loadGif(self, gif):
        
        lab     = QtWidgets.QLabel()
        gif.start()
        lab.setMovie(gif)
        lab.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.scene.addWidget(lab)