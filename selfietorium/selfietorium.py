#!/usr/bin/python
from lxml import etree as ET
from lxml.etree import QName
import array
import math
import cairo
import pygame
import pygame.display
#import pygame.camera
import picamera # This is the pi cam import
import RPi.GPIO as GPIO # This is the GPIO stuff for buttons
import rsvg
import PIL.Image
import sys
from libselfietorium import template
from libselfietorium import configuration
from libselfietorium import pygameTextRectangle
from libselfietorium import SendTweet

import datetime
import base64
import StringIO
import os
import traceback

# Constants
WIDTH = 640                     # Width of the window
HEIGHT = 480                    # Height of the window
SHOOTDIRECTORY = None           # Name of directory to store photographs taken
PHOTOSOUNDEFFECT = None         # Sound effect to play when taking photo
SCREEN_ATTRACT = None           # Attract Screen SVG XML data
CAMERASOUND = None              # Camera noise to play when taking a photo.
SCREEN_FONT = None
FONT_COLOUR = None              # Colour to display updated text to subjects
TWEET_TEXT = ""                 # Default tweet text to use when
                                # tweeting pictures.


def bgra_rgba(surface):
        img = PIL.Image.frombuffer('RGBA', (surface.get_width(),
              surface.get_height()), surface.get_data(),
              'raw', 'BGRA', 0, 1)
        return img.tobytes('raw', 'RGBA', 0, 1)


def load_svg_string(svg_data):
    svg = rsvg.Handle(data=svg_data)
    img_w, img_h = svg.props.width, svg.props.height
    scale_factorx = float(WIDTH) / float(img_w)
    scale_factory = float(HEIGHT) / float(img_h)
    surface = cairo.ImageSurface(cairo. FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)
    ctx.scale(scale_factorx, scale_factory)
    svg.render_cairo(ctx)
    return pygame.image.frombuffer(bgra_rgba(surface), (WIDTH, HEIGHT), 'RGBA')


def load_svg(filename):
    """Render SVG as Pygame image"""
    svg = rsvg.Handle(filename)
    img_w, img_h = svg.props.width, svg.props.height
    scale_factorx = float(WIDTH) / float(img_w)
    scale_factory = float(HEIGHT) / float(img_h)
    surface = cairo.ImageSurface(cairo. FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)
    ctx.scale(scale_factorx, scale_factory)

    svg.render_cairo(ctx)
    return pygame.image.frombuffer(bgra_rgba(surface), (WIDTH, HEIGHT), 'RGBA')


# This is a poor state implementation - a better implementation will be
#worked out in due course
#Valid States are :
#
# ATTRACT
# PREEN
# PHOTO
# COMPOSITE
# PRINT
#
def setup_GPIO():
    GPIO.setmode(GPIO.BCM)
    #Set up the pins
    GPIO.setup(12,GPIO.IN,pull_up_down = GPIO.PUD_UP)
    GPIO.setup(26,GPIO.IN,pull_up_down = GPIO.PUD_UP)
    GPIO.setup(4,GPIO.OUT)
    GPIO.output(4,GPIO.LOW)

def picam_get_photo(cam):
    img = cam.get_image()
    return img

def TakePhoto ():
    with picamera.PiCamera() as camera:
        camera.start_preview()
        time.sleep(0)
        GPIO.output(4,GPIO.HIGH)
        camera.capture('/home/pi/Desktop/image.jpg')
        camera.stop_preview()
        GPIO.output(4,GPIO.LOW)



def convert_surface_to_image(surface):
    pil = pygame.image.tostring(surface, "RGBA", False)
    img = PIL.Image.frombytes("RGBA", (640, 480), pil)
    return img


def savephoto(mydir, img_photo, filename):
    """Saves a photo as filename in the folder specified"""
    try:
        os.makedirs(mydir)
    except OSError, e:
        if e.errno != 17:
            raise     # This was not a "directory exist" error..
    img_photo = convert_surface_to_image(img_photo)
    img_photo.save(os.path.join(mydir, filename), format="PNG")


def layout(tplate, photos, outputdir):
    """Layout template and save to Directory"""
    update_node = tplate
    for shot in photos:
        imgPhoto = convert_surface_to_image(shot.photo)
        output = StringIO.StringIO()
        imgPhoto.save(output, format="PNG")
        contents = output.getvalue()
        output.close()
        photoB64 = pygame.image.tostring(shot.photo, "RGB")
        photoB64 = contents
        base64data = base64.b64encode(contents)
        str_b64 = "data:image/png;base64," + base64data
        update_node = template.updateNodeAttrib(update_node, shot.imageID,
            "{http://www.w3.org/1999/xlink}href", str_b64)
    text_file = open(os.path.join(outputdir, "Output.svg"), "w")
    text_file.write(update_node)
    text_file.close()
    save_svg_to_img(update_node, outputdir, "Composite.png")
    return os.path.join(outputdir, "Composite.png")

# Screen methods


def save_svg_to_img(svg, outputdir, filename):
    IMG = load_svg_string(svg)
    screen.blit(cbackground, (0, 0))
    screen.blit(IMG, (0, 0))
    pygame.display.flip()
    pygame.time.delay(5000)
    savephoto(outputdir, IMG, filename)


def preen_screen(photoshoot, svg_data, preentime=10):
    screenGeometry = template.findGeometry(svg_data)
    scaleWidth = float(float(WIDTH) / float(screenGeometry[0]))
    scaleHeight = float(float(HEIGHT) / float(screenGeometry[1]))
    picam = template.findNode(svg_data, '//svg:rect[@id="picam"]')
    pcamWidth = int(math.ceil(float(picam.attrib['width']) * scaleWidth))
    pcamHeight = int(math.ceil(float(picam.attrib['height']) * scaleHeight))
    picamx = int(math.floor(float(picam.attrib['x']) * scaleWidth))
    picamy = int(math.floor(float(picam.attrib['y']) * scaleHeight))

    prompt = template.findNode(svg_data, '//svg:rect[@id="prompt"]')
    svg_data = template.deleteNode(svg_data, '//svg:rect[@id="prompt"]')

    promptfont = template.findNode(svg_data, '//svg:text[@id="promptfont"]')
    svg_data = template.deleteNode(svg_data, '//svg:text[@id="promptfont"]')

    promptx = int(math.floor(float(prompt.attrib['x']) * scaleWidth))
    prompty = int(math.floor(float(prompt.attrib['y']) * scaleHeight))
    promptWidth = int(math.ceil(float(prompt.attrib['width']) * scaleWidth))
    promptHeight = int(math.ceil(float(prompt.attrib['height']) * scaleHeight))
    promptBackground = prompt.attrib['style']

    for shot in photoshoot:
        photo = picam_get_photo(cam)
        my_font = pygame.font.SysFont(SCREEN_FONT, SCREEN_FONT_SIZE)
        my_string = str(shot.title) or config.prePhotoPhrase
        my_rect = pygame.Rect((promptx, prompty, promptWidth, promptHeight))
        prompt = pygameTextRectangle.render_textrect(my_string, my_font,
            my_rect, SCREEN_FONT_COLOUR, (0, 0, 0, 0), 1)
        start = datetime.datetime.now()
        end = datetime.datetime.now()

        preentimeSpent = (end - start).seconds
        while preentime - preentimeSpent > 0:
            photo = picam_get_photo(cam)
            end = datetime.datetime.now()
            preentimeSpent = (end - start).seconds
            if preentime - preentimeSpent == 0:
                break
            svg_data = template.updateNode(svg_data, 'countDown',
                                               str(preentime - preentimeSpent))
            IMG = load_svg_string(svg_data)
            screen.blit(background, (0, 0))
            screen.blit(IMG, (0, 0))
            screen.blit(pygame.transform.scale(photo,
                             (pcamWidth, pcamHeight)), (picamx, picamy))
            shot.image = photo
            screen.blit(prompt, (promptx, prompty))
            pygame.display.flip()
            pygame.time.delay(25)
        CAMERASOUND.play()
        shot.photo = photo
        savephoto(SHOOTDIRECTORY, photo, shot.imageID + ".png")
        pygame.time.delay(500)
        screen.blit(background, (0, 0))
        screen.blit(pygame.transform.scale(photo, (WIDTH, HEIGHT)), (0, 0))
        pygame.display.flip()
        pygame.time.delay(2000)

    # Cache this...
    tphotoshoot = svg_data = open(config.layout).read()
    composite = layout(tphotoshoot, photoshoot, SHOOTDIRECTORY)
    print ('Composite png located at ' + composite)
    SocialMedia.tweetPhoto(TWEET_TEXT, composite)
    return "ATTRACT"


def attract_screen(attract_svg_data):
    IMG = load_svg_string(attract_svg_data)
    screen.blit(background, (0, 0))
    screen.blit(IMG, (0, 0))
    pygame.display.flip()


def error_screen(error_svg_data, xception):
    print error_svg_data    
    print "error_svg_data"    
    my_font = pygame.font.SysFont(ERROR_FONT, SCREEN_FONT_SIZE)
    my_string = "an error has occured"
    screenGeometry = template.findGeometry(error_svg_data)
    scaleWidth = float(float(WIDTH) / float(screenGeometry[0]))
    scaleHeight = float(float(HEIGHT) / float(screenGeometry[1]))
    prompt = template.findNode(error_svg_data, '//svg:rect[@id="ErrorMessage"]')
    error_svg_data = template.deleteNode(error_svg_data, '//svg:rect[@id="ErrorMessage"]')

    #IMG = load_svg_string(error_svg_data)

    #promptx = int(math.floor(float(prompt.attrib['x']) * scaleWidth))
    #prompty = int(math.floor(float(prompt.attrib['y']) * scaleHeight))
    #promptWidth = int(math.ceil(float(prompt.attrib['width']) * scaleWidth))
    #promptHeight = int(math.ceil(float(prompt.attrib['height']) * scaleHeight))
    #my_rect = pygame.Rect((promptx, prompty, promptWidth, promptHeight))
    #prompt = pygameTextRectangle.render_textrect(my_string, my_font, my_rect, ERROR_FONT_COLOUR, (0, 0, 0, 0), 1)
    #screen.blit(background, (0, 0))
    #screen.blit(IMG, (0, 0))
    #screen.blit(prompt, (promptx, prompty))
    #pygame.display.flip()
    #pygame.time.delay(1000)
    print ('Error :')
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback_template = '''Traceback (most recent call last):
      File "%(filename)s", line %(lineno)s, in %(name)s %(type)s: %(message)s\n'''
    traceback_details = {
                         'filename': exc_traceback.tb_frame.f_code.co_filename,
                         'lineno'  : exc_traceback.tb_lineno,
                         'name'    : exc_traceback.tb_frame.f_code.co_name,
                         'type'    : exc_type.__name__,
                         'message' : exc_value.message, # or see traceback._some_str()
                        }
    print()
    print(traceback.format_exc())
    print()
    print(traceback_template % traceback_details)
    print()


def debug_print_configuration(config, photoshoot):
    """Prints configuration to console."""
    print("Starting selfietorium...")
    print("------------------------")
    print()
    print("Configuration :")
    print()
    print("Template        : " + config.layout)
    print("Pre-PhotoPhrase : " + config.prePhotoPhrase)
    print("Preen Time      : " + str(config.preenTime) + " seconds.")
    print("Shutter Sound   : " + config.shutterSound)
    print("Photo store     : " + config.photostore)
    print("Pre-PhotoPhrase : " + config.prePhotoPhrase)
    print("Update Font     : " + config.Font)
    print("Update Font Size: " + str(config.Size))
    print("Update Font Colour: " + str(config.FontColour))
    print()
    print()


if __name__ == '__main__':
    #Set up configuration
    setup_GPIO()    
    config = configuration.ConfigFile("boothsettings.json")
    #SocialMedia = SendTweet.selfie_Tweet()

    config.Load()
    debug_print_configuration(config, None)
    #Set up variables
    SHOOTPHOTOSTORE = config.photostore
    SHOOTDIRECTORY = os.path.join(SHOOTPHOTOSTORE,
                         datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    SCREEN_FONT = config.Font
    SCREEN_FONT_SIZE = config.Size
    SCREEN_FONT_COLOUR = config.FontColour
    PHOTOSOUNDEFFECT = config.shutterSound
    TWEET_TEXT = config.TweetPhrase
    photoshoot = template.LoadPhotoShoot(config.layout)
    debug_print_configuration(config, photoshoot)

    #Set Up Screens
    SCREEN_ATTRACT = open('Screens/Attract.svg').read()
    SCREEN_PREEN = open('Screens/Instructions2.svg').read()
    SCREEN_ERROR = open('Screens/Error.svg').read()
    ERROR_FONT = config.ErrorFont
    ERROR_FONT_SIZE = config.ErrorFontSize
    ERROR_FONT_COLOUR = config.ErrorFontColour




    #pygame.camera.init()
    #cam = pygame.camera.Camera(pygame.camera.list_cameras()[0])
    #cam.start()
    cam= picamera.PiCamera() #as camera:

    state = "ATTRACT"
    pygame.init()
    pygame.mixer.init(48000, -16, 1, 1024)
    CAMERASOUND = pygame.mixer.Sound(PHOTOSOUNDEFFECT)
    #pygame.display.set_mode((WIDTH,HEIGHT),0,16)
    screen = pygame.display.set_mode((640, 480))
    pygame.mouse.set_visible(False)
    background = pygame.Surface((WIDTH, HEIGHT))
    background = background.convert()
    background.fill((0, 0, 0))

    cbackground = pygame.Surface((WIDTH, HEIGHT))
    cbackground = cbackground.convert()
    cbackground.fill((200, 255, 255))

    #SocialMedia.tweet('Starting Selfietorium...')
        
    c = pygame.time.Clock()
    while True:
        try:
            input_state = GPIO.input(12)
            if input_state ==False:
                print "Button1 Pressed"
                print "RUN PRINT"
            if state == "ATTRACT":
                state = "PREEN"
                if GPIO.input(26) == False:
                    pygame.quit()
                    sys.exit()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_p:
                        if state == "ATTRACT":
                            state = "PREEN"
                    elif event.key == pygame.K_s:
                        CAMERASOUND.play()
                    elif event.key == pygame.K_e:
                        #ErrorScreen(SCREEN_ERROR)
                        raise ValueError('A very specific bad thing happened')
                if state == "ATTRACT":
                    attract_screen(SCREEN_ATTRACT)
                if state == "PREEN":
                    state = preen_screen(photoshoot, SCREEN_PREEN,
                                        config.preenTime)
        except Exception as e:
            error_screen(SCREEN_ERROR, e)


    # c.tick(1)
