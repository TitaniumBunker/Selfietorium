#!/usr/bin/python
# coding=utf-8


from PIL import Image
import pygame

class FakeCamera:
    """A class for capturing images from a fake camera"""
    def __init__(self):
        """Constructor for this object."""
        print("Starting Fake Camera Object")
        self.cam = Image.open(open("libselfietorium/eagle.jpg",'rb'))
        self.cam2 = pygame.image.load("libselfietorium/eagle.jpg")
    
    def Configure(self,brightness,contrast,saturation):
        pass
    
    def GetPhoto(self,brightness,contrast,saturation):
        """
        Returns a photo from the camera (by default it should be an eagle picture)

        :return:
            A photo from the picamera, converted to a surface
        """
        return self.cam2

    def DisplayPreview(self,screen,pygame,picamx, picamy,pcamWidth, pcamHeight):
        screen.blit(pygame.transform.scale(self.cam2,(pcamWidth, pcamHeight)), (picamx, picamy))

if __name__ == '__main__':

    # Add sample Code here
    pass
