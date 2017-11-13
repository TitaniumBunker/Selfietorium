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

    def GetPhoto(self,brightness,contrast,saturation):
        """Return an image from the camera

        Returns:
            Image as a pygame surface

        """
        img = self.cam.get_image()
        return img



if __name__ == '__main__':

    # Add sample Code here
    pass
