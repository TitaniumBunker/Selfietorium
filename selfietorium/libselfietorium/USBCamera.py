#!/usr/bin/python
# coding=utf-8

import pygame.camera


class USBCamera:
    """A class for capturing images from a web camera"""
    def __init__(self):
        """Constructor for this object."""
        print("Starting USB Camera Object")
        pygame.camera.init()
        self.cam = pygame.camera.Camera(pygame.camera.list_cameras()[0])
        self.cam.start()
    
    def Configure(self,brightness,contrast,saturation):
        pass

    def GetPhoto(self,brightness,contrast,saturation):
        """Return an image from the camera

        Returns:
            Image as a pygame surface

        """
        self.cam.set_controls(brightness=brightness)
        img = self.cam.get_image()
        return img

    def DisplayPreview(self,screen,pygame,picamx, picamy,pcamWidth, pcamHeight):
        screen.blit(pygame.transform.scale(self.cam.get_image(),(pcamWidth, pcamHeight)), (picamx, picamy))


if __name__ == '__main__':

    # Add sample Code here
    pass
