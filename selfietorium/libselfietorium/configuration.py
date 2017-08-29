#!/usr/bin/python
# coding=utf-8
"""
A library that provides configuration loading and saving for the selfietorium project

This is a python library for handling the configuration for selfietorium.

Notes:
Pyxser is a library that aparently also provides object serialisation, but
attempts to locate this package in the repos has so far failed. This class
therefore provides specific serialisation methods mentioned in:
http://www.diveintopython3.net/serializing.html

Example:
    To Save a configuration file (which will have default values)::

     import configuration
     cfile = ConfigFile("boothsettings.json")
     c.Save()
"""
import json
from os.path import expanduser
import os.path

class ConfigFile:
    """A Configuration object - this object serialises / deserialises data to
    JSON format."""
    def __init__(self, iniFile):
        """Constructor for this object."""
        self.inifile = expanduser(iniFile)
        self.layout = 'Templates/Template1.svg'
        self.prePhotoPhrase = 'Smile'
        self.photostore = '~/Photos/'
        self.preenTime = 5
        self.Font = "MyUnderwood"
        self.Size = 30
        self.FontColour = [125, 125, 125]
        self.photosTaken = 0
        self.sheetspercartidge = 0
        self.shutterSound = "Assets/62491__benboncan__dslr-click.wav"
        self.ErrorFontColour = [0, 0, 0]
        self.ErrorFont = "MyUnderwood"
        self.ErrorFontSize = 20
        self.TweetPhrase = "I just took this photo... #selfietorium_test"
        self.CameraModule = "libselfietorium.USBCamera"
        self.CameraFile = "USBCamera"
        self.FlashModule = "libselfietorium.Flash"
        self.FlashFile = "Flash"
        self.PrinterName = "PDF"
        self.ACCESS_TOKEN = "<REPLACE THIS WITH YOUR ACCESS TOKEN>"
        self.ACCESS_SECRET = "<REPLACE THIS WITH YOUR ACCESS TOKEN SECRET>"
        self.CONSUMER_KEY = "<REPLACE THIS WITH YOUR API KEY>"
        self.CONSUMER_SECRET = "<REPLACE THIS WITH YOUR API SECRET>"
        self.TweetAuthor =  "<REPLACE THIS WITH THE SCREEN NAME OF THE ACCOUNT SELFIETORIUM TWEETS AS>"
        self.TweetHashTag =  "<REPLACE THIS WITH THE HASHTAG FOR TWEETS>"
        if os.path.isfile(self.inifile ) == False:
            self.Save()


    def Load(self):
        """Load data from config file into object."""
        with open(self.inifile, mode='r') as f:
            entry = json.load(f)
            self.layout = expanduser(entry['layout'])
            self.prePhotoPhrase = entry['prePhotoPhrase']
            self.photostore = expanduser(entry['PhotoStore'])
            self.preenTime = entry['preenTime']
            self.photosTaken = entry['photosTaken']
            self.sheetspercartidge = entry['sheetspercartidge']
            self.shutterSound = entry['shutterSound']
            self.Font = entry['Font']
            self.Size = entry['Size']
            self.FontColour = entry['FontColour']
            self.ErrorFontColour = entry['ErrorFontColour']
            self.ErrorFont = entry['ErrorFont']
            self.ErrorFontSize = entry['ErrorFontSize']
            self.TweetPhrase = entry['TweetPhrase']
            self.CameraModule = entry['CameraModule']
            self.CameraFile = entry['CameraFile']
            self.FlashModule = entry['FlashModule']
            self.FlashFile = entry['FlashFile']
            self.PrinterName = entry['PrinterName']
            self.ACCESS_TOKEN = entry['ACCESS_TOKEN']
            self.ACCESS_SECRET = entry['ACCESS_SECRET']
            self.CONSUMER_KEY = entry['CONSUMER_KEY']
            self.CONSUMER_SECRET = entry['CONSUMER_SECRET']
            self.TweetAuthor = entry["TweetAuthor"]
            self.TweetHashTag = entry["TweetHashTag"]
            return entry

    def Save(self):
        """Save data to config file."""
        configuration = {}
        configuration['layout'] = self.layout
        configuration['prePhotoPhrase'] = self.prePhotoPhrase
        configuration['PhotoStore'] = self.photostore
        configuration['preenTime'] = self.preenTime
        configuration['photosTaken'] = self.photosTaken
        configuration['sheetspercartidge'] = self.sheetspercartidge
        configuration['shutterSound'] = self.shutterSound
        configuration['FontColour'] = self.FontColour
        configuration['Size'] = self.Size
        configuration['Font'] = self.Font
        configuration['ErrorFontColour'] = self.ErrorFontColour
        configuration['ErrorFont'] = self.ErrorFont
        configuration['ErrorFontSize'] = self.ErrorFontSize
        configuration['TweetPhrase'] = self.TweetPhrase
        configuration['CameraModule'] = self.CameraModule
        configuration['CameraFile'] = self.CameraFile
        configuration['FlashModule'] = self.FlashModule
        configuration['FlashFile'] = self.FlashFile
        configuration['PrinterName'] = self.PrinterName
        configuration['ACCESS_TOKEN'] = self.ACCESS_TOKEN
        configuration['ACCESS_SECRET'] = self.ACCESS_SECRET
        configuration['CONSUMER_KEY'] = self.CONSUMER_KEY
        configuration['CONSUMER_SECRET'] = self.CONSUMER_SECRET
        configuration['TweetAuthor'] = self.TweetAuthor
        configuration['TweetHashTag'] = self.TweetHashTag
        print self.inifile
        with open(self.inifile, mode='w') as f:
            json.dump(configuration, f, indent=2)


if __name__ == '__main__':
    c = ConfigFile("~/boothsettings.test.json")

    c.Save()
    config = c.Load()
