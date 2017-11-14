#!/usr/bin/python
# coding=utf-8
#
# based on information gleaned from http://raspberrypi.stackexchange.com/questions/24232/picamera-taking-pictures-fast-and-processing-them
import picamera
import io
import pygame
from PIL import Image


class PicamCamera:
    """A class for capturing images from Picam"""
    def __init__(self):
        """Constructor for this object."""
        print("Starting picam Camera Object")
        self.cam = picamera.PiCamera()
        #self.stream = io.BytesIO()
        self.previewing = False

    def Configure(self,brightness,contrast,saturation):
        self.cam.brightness = brightness
        self.cam.contrast = contrast
        self.cam.saturation = saturation

    def DisplayPreview(self,screen,pygame,picamx, picamy,pcamWidth, pcamHeight):
        if (self.previewing == False):
            Window = pygame.transform.scale(self.GetPhoto(self.cam.brightness,self.cam.contrast,self.cam.saturation),(pcamWidth, pcamHeight))
            self.cam.start_preview(fullscreen=False, window = (picamx, picamy, pcamWidth, pcamHeight))

    def HidePreview(self):
        self.cam.stop_preview()
        self.previewing = False

    def GetPhoto(self,brightness,contrast,saturation):
        """
        Returns a photo from the PiCam module.

        :return:
            A photo from the picamera, converted to a surface
        """
        self.cam.brightness = brightness
        self.cam.contrast = contrast
        self.cam.saturation = saturation

	with io.BytesIO() as self.stream:
		self.cam.capture(self.stream, format='jpeg', use_video_port=False)
        	#camera.capture(stream, format='jpeg', use_video_port=True)
		self.stream.seek(0)
        	image = Image.open(self.stream)
		mode = image.mode
		size = image.size
		data = image.tobytes()
		return pygame.image.fromstring(data, size, mode)

if __name__ == '__main__':

    # Add sample Code here
    pass
