#!/usr/bin/python
# coding=utf-8
import importlib
import math
import cairo
import pygame
import pygame.display
import rsvg
import PIL.Image
import sys
from libselfietorium import template
from libselfietorium import configuration
from libselfietorium import pygameTextRectangle
from libselfietorium import SendTweet
from libselfietorium import utilities
import datetime
import base64
import StringIO
import os
from os.path import dirname
import traceback
GPIO_IMPORTED = False
try:
    import RPi.GPIO as GPIO
    GPIO_IMPORTED = True
except ImportError:
    print("Unable to import GPIO")


class GetOutOfLoop( Exception ):
    """Exception used to allow Selfietorium to exit loops."""
    pass


class ScreenElelement():

    """
    Object that describes a screen element, and its position on the screen.

    """

    def __init__(self, image, x, y):
        self.image = image
        self.x = x
        self.y = y


class mainclass():





    """
    Main code for Selfietorium.
    """

    def __init__(self):
        # Constants
        #size = pygame.display.list_modes()[0]
#screen = pygame.display.set_mode(size,pg.FULLSCREEN)
        self.WIDTH = 720                    # Width of the window
        self.HEIGHT = 576                    # Height of the window
        self.DPI = 90                        # Recalculate this based on your screen.
        self.SHOOTDIRECTORY = None           # Name of directory to store photographs taken
        self.PHOTOSOUNDEFFECT = None         # Sound effect to play when taking photo
        self.SCREEN_ATTRACT = None           # Attract Screen SVG XML data
        self.CAMERASOUND = None              # Camera noise to play when taking a photo.
        self.SCREEN_FONT = None
        self.FONT_COLOUR = None              # Colour to display updated text to subjects
        self.TWEET_TEXT = ""                 # Default tweet text to use when
                                             # tweeting pictures.
        self.mymethod = None
        self.flashmethod = None                    # Flash.... Ahhh Saviour of the Universe
        self.background = None               # black image for clearing the screen
        self.CONFIGURATION = None
        #GPIO SETUP
        if (GPIO_IMPORTED):
            GPIO.setmode(GPIO.BCM)     # set up BCM GPIO numbering  
            GPIO.setup(26, GPIO.IN,pull_up_down=GPIO.PUD_UP)    # set GPIO 25 as input  
            GPIO.setup(12, GPIO.IN,pull_up_down=GPIO.PUD_UP)    # set GPIO 12 as input
            GPIO.setup(4,  GPIO.OUT)
        
    def bgra_rgba(self, surface):
        """

        :param surface:
        :return:
        """
        img = PIL.Image.frombuffer('RGBA', (surface.get_width(),
              surface.get_height()), surface.get_data(),
              'raw', 'BGRA', 0, 1)
        return img.tobytes('raw', 'RGBA', 0, 1)

    def load_svg_string(self, svg_data):
        """

        :param svg_data:
        :return:
        """
	
        svg = rsvg.Handle(data=svg_data)
        img_w, img_h = svg.props.width, svg.props.height
        scale_factorx = float(self.WIDTH) / float(img_w)
        scale_factory = float(self.HEIGHT) / float(img_h)
        surface = cairo.ImageSurface(cairo. FORMAT_ARGB32, self.WIDTH, self.HEIGHT)
        ctx = cairo.Context(surface)
        ctx.scale(scale_factorx, scale_factory)
        svg.render_cairo(ctx)
        return pygame.image.frombuffer(self.bgra_rgba(surface), (self.WIDTH, self.HEIGHT), 'RGBA')

    def load_svg(self, filename):
        """Render SVG as Pygame image"""
        svg = rsvg.Handle(filename)
        img_w, img_h = svg.props.width, svg.props.height
        scale_factorx = float(self.WIDTH) / float(img_w)
        scale_factory = float(self.HEIGHT) / float(img_h)
        surface = cairo.ImageSurface(cairo. FORMAT_ARGB32, self.WIDTH, self.HEIGHT)
        ctx = cairo.Context(surface)
        ctx.scale(scale_factorx, scale_factory)
        svg.render_cairo(ctx)
        return pygame.image.frombuffer(self.bgra_rgba(surface), (self.WIDTH,self.HEIGHT), 'RGBA')


    def photo_to_b64(self,photo):
        imgPhoto = self.convert_surface_to_image(photo)
        output = StringIO.StringIO()
        imgPhoto.save(output, format="PNG")
        contents = output.getvalue()
        output.close()
        base64data = base64.b64encode(contents)
        str_b64 = "data:image/png;base64," + base64data
        return str_b64
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


    def convert_surface_to_image(self, surface):
        """

        :param surface:
        :return:
        """
        width = surface.get_width() # 640
        height = surface.get_height() # 480
        pil = pygame.image.tostring(surface, "RGBA", False)
        img = PIL.Image.frombytes("RGBA", (width, height), pil)
        return img

    def savephoto(self, mydir, img_photo, filename):
        """Saves a photo as filename in the folder specified"""
        try:
            os.makedirs(mydir)
        except OSError, e:
            if e.errno != 17:
                raise     # This was not a "directory exist" error..
        img_photo = self.convert_surface_to_image(img_photo)
        img_photo.save(os.path.join(mydir, filename), format="PNG")


    def layout(self,tplate, photos, outputdir):
        """Layout template and save to Directory"""
        update_node = tplate
        for shot in photos:
            imgPhoto = self.convert_surface_to_image(shot.photo)
            output = StringIO.StringIO()
            imgPhoto.save(output, format="PNG")
            contents = output.getvalue()
            output.close()
            base64data = base64.b64encode(contents)
            str_b64 = "data:image/png;base64," + base64data
            update_node = template.updateNodeAttrib(update_node, shot.imageID,
                "{http://www.w3.org/1999/xlink}href", str_b64)
        text_file = open(os.path.join(outputdir, "Output.svg"), "w")
        text_file.write(update_node)
        text_file.close()
        self.save_svg_to_img(update_node, outputdir, "Composite.png")
        return os.path.join(outputdir, "Composite.png")

# Screen methods
    def save_svgfile_to_img(self, outputdir, svgfile, destination_outputdir, destination_filename):
        """
        :param svg:
        :param outputdir:
        :param filename:
        """
	cmf = 'convert %s %s' % ( os.path.join(outputdir, svgfile), os.path.join(destination_outputdir, destination_filename))
	     
	import subprocess
	subprocess.call (cmf,preexec_fn=os.setsid, shell=True)
	IMG = pygame.image.load(os.path.join(destination_outputdir, destination_filename))	
	IMG = pygame.transform.scale(IMG, pygame.Rect((0,0),(self.WIDTH, self.HEIGHT)).size)
	IMG = IMG.convert()
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(IMG, (0, 0))
        pygame.display.flip()
        pygame.time.delay(2000)


    def save_svg_to_img(self, svg, outputdir, filename):
        """

        :param svg:
        :param outputdir:
        :param filename:
        """
        IMG = self.load_svg_string(svg)
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(IMG, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5000)
        self.savephoto(outputdir, IMG, filename)

    def load_image_from_url_as_B64(self,source):
        """

        :param source:
        :return:
        """
        from urllib2 import urlopen
        import io
        image_str = urlopen(source).read()
        image_file = io.BytesIO(image_str)
        avatar = pygame.image.load(image_file)
        result = self.convert_surface_to_image(avatar)
        output = StringIO.StringIO()
        result.save(output, format="PNG")
        contents = output.getvalue()
        output.close()
        base64data = base64.b64encode(contents)
        str_b64 = "data:image/png;base64," + base64data
        return str_b64

    def twitter_latest(self, svg, imagesvg):
        """
        Twitter Screen - displays the latest tweet.
        :param svg:
        :param imagesvg:
        """
        screenElements = []
        try:
            svg_loaded = rsvg.Handle(data=svg)
            img_w, img_h = svg_loaded.props.width, svg_loaded.props.height
            scale_factorx = float(self.WIDTH) / float(img_w)
            scale_factory = float(self.HEIGHT) / float(img_h)
            latest_tweet = self.SocialMedia.latest_Tweet

            if latest_tweet != None:
                from HTMLParser import HTMLParser
                h = HTMLParser()
                str_b64 = self.load_image_from_url_as_B64(latest_tweet.user.profile_image_url)
                #Update Avatar
                svg = template.updateNodeAttrib(svg, "twitter_avatar",
                    "{http://www.w3.org/1999/xlink}href", str_b64)
                #Update Twitter name
                svg = template.updateNode(svg, 'twitter_name',latest_tweet.user.name)
                #Update Twitter handle
                svg = template.updateNode(svg, 'twitter_handle','@'+latest_tweet.user.screen_name)
                #Update Twitter handle
                #svg = template.updateNode(svg, 'twitter_tweet',the_dict['text'])
                #update Tweet
                screenGeometry = template.findGeometry(svg)
                scaleWidth = float(float(self.WIDTH) / float(screenGeometry[0]))
                scaleHeight = float(float(self.HEIGHT) / float(screenGeometry[1]))
                prompt = template.findNode(svg, '//svg:rect[@id="twitter_tweet_region"]')
                promptFont = template.findNode(svg, '//svg:text[@id="twitter_tweet_region_font"]')

                # what does this do?
                #s = promptFont.attrib['style']
                #s = s.rstrip(';')
                #styles = dict(item.split(":") for item in s.split(";"))
                #SCREEN_FONT = styles["font-family"]
                styles = template.get_Element_Styles(promptFont)
                SCREEN_FONT = styles["font-family"]
                SCREEN_FONT_SIZE = int(''.join(c for c in styles["font-size"] if c.isdigit()))
                SCREEN_FONT_SIZE = int(round((float(SCREEN_FONT_SIZE)) * float(scale_factorx)))
                #points = (pixels / 150) * 72
                self.SCREEN_FONT_COLOUR = styles["fill"][1:]
                self.SCREEN_FONT_COLOUR  = self.util.hex_to_rgb(self.SCREEN_FONT_COLOUR)
                svg = template.deleteNode(svg, '//svg:rect[@id="twitter_tweet_region"]')
                promptx = int(math.floor(float(prompt.attrib['x']) * scaleWidth))
                prompty = int(math.floor(float(prompt.attrib['y']) * scaleHeight))
                promptWidth = int(math.ceil(float(prompt.attrib['width']) * scaleWidth))
                promptHeight = int(math.ceil(float(prompt.attrib['height']) * scaleHeight))
                twitter_rect = pygame.Rect((promptx, prompty, promptWidth, promptHeight))
                my_font = pygame.font.SysFont(SCREEN_FONT, SCREEN_FONT_SIZE)
                prompt = pygameTextRectangle.render_textrect(h.unescape(latest_tweet.text), my_font, twitter_rect, self.SCREEN_FONT_COLOUR, (0, 0, 0, 0), 0)
                IMG = self.load_svg_string(svg)
                screenElements.append(ScreenElelement(self.background,0,0))
                screenElements.append(ScreenElelement(IMG,0,0))
                screenElements.append(ScreenElelement(prompt,promptx, prompty))
                self.show_screen_elements(screenElements,1)
                if 'media' in latest_tweet.entities:
                    for image in latest_tweet.entities['media']:
                        imagesvg = template.updateNodeAttrib(imagesvg, "twitter_avatar","{http://www.w3.org/1999/xlink}href", str_b64)
                        imagesvg = template.updateNode(imagesvg, 'twitter_name',latest_tweet.user.name)
                        photo_b64 = self.load_image_from_url_as_B64(image['media_url'])
                        imagesvg = template.updateNodeAttrib(imagesvg, "twitter_photo","{http://www.w3.org/1999/xlink}href", photo_b64)
                        IMG = self.load_svg_string(imagesvg)
                        screenElements.append(ScreenElelement(IMG,0,0))
                        self.show_screen_elements(screenElements,1)
        except GetOutOfLoop:
            print "Exception - GET OUT OF LOOP"
            pass

    def show_screen_elements(self,elemenets,time):
        """
        Shows screen elements on the screen for a period of time.
        :param elemenets: List of ScreenElements to show on the screen.
        :param time: Time in Seconds
        """
        start = pygame.time.get_ticks()
        while  pygame.time.get_ticks() - start < (time *1000):
            self.event_logic()
            for screenelement in elemenets:
                self.screen.blit(screenelement.image, (screenelement.x, screenelement.y))
            pygame.display.flip()
            pygame.time.delay(25)
            self.c.tick(30)

    def show_screen(self,IMG,time):
        """
        Shows a screen for a number of seconds
        :param IMG:
        :param time:
        """
        start = pygame.time.get_ticks()
        while  pygame.time.get_ticks() - start < (time *1000):
            self.event_logic()
            self.screen.blit(IMG, (0, 0))
            pygame.display.flip()
            self.c.tick(30)

    def event_logic(self):
        """
        Event logic - determining what events to activate based on key presses.
        """
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_q) or (not GPIO.input(12)):
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_p : #or
                #elif not GPIO.input(26):
                    if self.state == "ATTRACT" or self.state =="TWEET" :
                        self.state = "PREEN"
                        raise GetOutOfLoop
                elif event.key == pygame.K_s:
                    self.CAMERASOUND.play()
                elif event.key == pygame.K_t:
                    self.state = "TWEET"
                elif event.key == pygame.K_e:
                    raise ValueError('A very specific bad thing happened')





    def configure(self, photoshoot, svg_data, preentime=10):
        quit = False    
        self.flashmethod.flash_on()
        screenGeometry = template.findGeometry(svg_data)
        scaleWidth = float(float(self.WIDTH) / float(screenGeometry[0]))
        scaleHeight = float(float(self.HEIGHT) / float(screenGeometry[1]))
        picam = template.findNode(svg_data, '//svg:rect[@id="picam"]')
        pcamWidth = int(math.ceil(float(picam.attrib['width']) * scaleWidth))
        pcamHeight = int(math.ceil(float(picam.attrib['height']) * scaleHeight))
        picamx = int(math.floor(float(picam.attrib['x']) * scaleWidth))
        picamy = int(math.floor(float(picam.attrib['y']) * scaleHeight))
        
        brighness = 50
        contrast = 50
        sturation = 50

        while quit == False:
               for event in pygame.event.get():
                     
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_x:
                            quit = True
                        if event.key == pygame.K_g:
                            quit = True
                        if event.key == pygame.K_w:
                            brighness = min(brighness + 1, 100)
                        if event.key == pygame.K_s:
                            brighness = max(brighness - 1, 0)
                    
                        if event.key == pygame.K_e:
                            contrast = min(contrast + 1, 100)
                        if event.key == pygame.K_d:
                            contrast = max(contrast - 1, 0)
                                            
                        if event.key == pygame.K_r:
                            sturation = min(sturation + 1, 100)
                        if event.key == pygame.K_f:
                            sturation = max(sturation - 1, 0)

                    svg_data = template.updateNode(svg_data, 'brightness',str(brighness))
                    svg_data = template.updateNode(svg_data, 'contrast',str(contrast))
                    svg_data = template.updateNode(svg_data, 'saturation',str(sturation))

                    photo = self.mymethod.GetPhoto(brighness,contrast,sturation)
                    IMG = self.load_svg_string(svg_data)
                    self.screen.blit(IMG, (0, 0))
                    self.screen.blit(pygame.transform.scale(photo,
                                     (pcamWidth, pcamHeight)), (picamx, picamy))

                    pygame.display.flip()
                    pygame.time.delay(1)

    def preen_screen(self, photoshoot, svg_data, preentime=10):
        """
        Preen Screen - allows the subjects the time to pose and get ready for their photo.
        :param photoshoot:
        :param svg_data:
        :param preentime:
        :return:
        """
        try:
            ShootTime = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            self.SHOOTDIRECTORY = os.path.join(self.SHOOTPHOTOSTORE, ShootTime)
            screenGeometry = template.findGeometry(svg_data)
            scaleWidth = float(float(self.WIDTH) / float(screenGeometry[0]))
            scaleHeight = float(float(self.HEIGHT) / float(screenGeometry[1]))
            
            picam = template.findNode(svg_data, '//svg:rect[@id="picam"]')
            pcamWidth = int(math.ceil(float(picam.attrib['width']) * scaleWidth))
            pcamHeight = int(math.ceil(float(picam.attrib['height']) * scaleHeight))
            picamx = int(math.floor(float(picam.attrib['x']) * scaleWidth))
            picamy = int(math.floor(float(picam.attrib['y']) * scaleHeight))
            prompt = template.findNode(svg_data, '//svg:rect[@id="prompt"]')

            svg_data = template.deleteNode(svg_data, '//svg:rect[@id="prompt"]')
            svg_data = template.deleteNode(svg_data, '//svg:text[@id="promptfont"]')

            promptx = int(math.floor(float(prompt.attrib['x']) * scaleWidth))
            prompty = int(math.floor(float(prompt.attrib['y']) * scaleHeight))
            promptWidth = int(math.ceil(float(prompt.attrib['width']) * scaleWidth))
            promptHeight = int(math.ceil(float(prompt.attrib['height']) * scaleHeight))

            for shot in photoshoot:
                print (str(self.SCREEN_FONT))
                p	
                if not pygame.font:
                    raise RuntimeError("no pygame font module")
                if not pygame.font.get_init():
                    pygame.font.init()
                if not pygame.font.get_init():
                    raise RuntimeError("pygame doesn't init")
                my_font = pygame.font.SysFont(None, self.SCREEN_FONT_SIZE)
                #my_font=pygame.font.SysFont("FreeMono",50)
                #my_font = pygame.font.Font("/home/mike/.local/share/fonts/MyUnderwood.ttf",30)
                my_string = str(shot.title) or self.CONFIGURATION.prePhotoPhrase
                my_rect = pygame.Rect((promptx, prompty, promptWidth, promptHeight))
                print ("Taking a photo" + my_string)
                print str(dir(my_font))
		#//my_font = pygame.font.Font(None, 22)
                print pygame.font.match_font('MyUnderwood')
                #if (pygame.font.match_font('MyUnderwood') != None):
                DIRNAME = os.path.join(dirname(__file__), "resources",)
                #my_font = pygame.font.Font('/home/mike/.local/share/fonts/MyUnderwood.ttf', 30)
                #my_font = pygame.font.Font((os.path.join(DIRNAME, "font", "MyUnderwood.ttf"), 8))
		#my_string = "Hi there! I'm a nice bit of wordwrapped text. Won't you be my friend? Honestly, wordwrapping is easy, with David's fancy new render_textrect () function.\nThis is a new line.\n\nThis is another one.\n\n\nAnother line, you lucky dog."
                #my_rect = pygame.Rect((40, 40, 300, 300))
                #prompt = pygameTextRectangle.render_textrect(my_string, my_font, my_rect, (216, 216, 216), (48, 48, 48), 0)
		prompt = pygameTextRectangle.render_textrect(my_string, my_font,
                    my_rect, self.SCREEN_FONT_COLOUR, (0, 0, 0, 0), 1)
                start = datetime.datetime.now()
                end = datetime.datetime.now()

                preentimeSpent = (end - start).seconds
                while preentime - preentimeSpent > 0:
                    photo = self.mymethod.GetPhoto()
                    end = datetime.datetime.now()
                    preentimeSpent = (end - start).seconds
		    #if preentime - preentimeSpent < 3:
                    self.flashmethod.flash_on()	
                    if preentime - preentimeSpent < 1:
                        shot.image = photo
                        break
                    svg_data = template.updateNode(svg_data, 'countDown',
                                                       str(preentime - preentimeSpent))
                    IMG = self.load_svg_string(svg_data)
                    self.screen.blit(IMG, (0, 0))
                    self.screen.blit(prompt, my_rect.topleft)
                    self.screen.blit(pygame.transform.scale(photo,
                                     (pcamWidth, pcamHeight)), (picamx, picamy))
                    #shot.image = photo
                    pygame.display.flip()
                    pygame.time.delay(1)
                self.CAMERASOUND.play()
                self.flashmethod.flash_off()
                shot.photo = photo
                self.savephoto(self.SHOOTDIRECTORY, photo, shot.imageID + ".png")
                pygame.time.delay(500)
                self.screen.blit(pygame.transform.scale(photo, (self.WIDTH, self.HEIGHT)), (0, 0))
                pygame.display.flip()
                pygame.time.delay(2000)

            # Cache this...
            tphotoshoot = svg_data = open(self.CONFIGURATION.layout).read()
            composite = self.layout(tphotoshoot, photoshoot, self.SHOOTDIRECTORY)
            print('Composite png located at ' + composite)
            try:
                self.SocialMedia.tweetPhoto(self.TWEET_TEXT, composite)
            except Exception as e:
                print str(e)
                pass # In the event of an error tweeting, carry on
            try:
		print "Printing ... " + composite
		self.PRINTER.print_photo(composite, 'test-' + ShootTime)
            except:
		pass # In the event that it couldn't print, carry on

	    #//c.print_photo('output.svg','test')
        except GetOutOfLoop:
            pass
        except Exception as e:
            self.error_screen(self.SCREEN_ERROR, e)

        finally:
            return "ATTRACT"

    def attract_screen(self, attract_svg_data):
        """

        :param attract_svg_data:
        """
        IMG = self.load_svg_string(attract_svg_data)
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(IMG, (0, 0))
        pygame.display.flip()
        #c.tick(40)

    def error_screen(self, error_svg_data, xception):
        """

        :param error_svg_data:
        :param xception:
        """
        screenElements = []
        my_font = pygame.font.SysFont(self.ERROR_FONT, self.SCREEN_FONT_SIZE)
        my_string = "an error has occured"
        screenGeometry = template.findGeometry(error_svg_data)
        scaleWidth = float(float(self.WIDTH) / float(screenGeometry[0]))
        scaleHeight = float(float(self.HEIGHT) / float(screenGeometry[1]))
        prompt = template.findNode(error_svg_data, '//svg:rect[@id="ErrorMessage"]')
        error_svg_data = template.deleteNode(error_svg_data, '//svg:rect[@id="ErrorMessage"]')
        IMG = self.load_svg_string(error_svg_data)
        promptx = int(math.floor(float(prompt.attrib['x']) * scaleWidth))
        prompty = int(math.floor(float(prompt.attrib['y']) * scaleHeight))
        promptWidth = int(math.ceil(float(prompt.attrib['width']) * scaleWidth))
        promptHeight = int(math.ceil(float(prompt.attrib['height']) * scaleHeight))
        my_rect = pygame.Rect((promptx, prompty, promptWidth, promptHeight))
        prompt = pygameTextRectangle.render_textrect(my_string, my_font, my_rect, self.ERROR_FONT_COLOUR, (0, 0, 0, 0), 1)
        screenElements.append(ScreenElelement(self.background,0,0))
        screenElements.append(ScreenElelement(IMG,0,0))
        screenElements.append(ScreenElelement(prompt,promptx, prompty))
        self.show_screen_elements(screenElements,1)
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
        self.state = "ATTRACT"









    def debug_print_configuration(self, config, photoshoot):
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
        print("Printer Name     :" + str(config.PrinterName))
        print("Twitter Screen Name:" + str(config.TweetAuthor))
        print("Twitter Hashtag     :" + str(config.TweetHashTag))

        print()
        print()

    def main_loop(self):
        #Set up configuration
        """
        main pygame loop.
        """
        self.CONFIGURATION = configuration.ConfigFile("~/boothsettings.json")
        self.CONFIGURATION .Load()

        self.debug_print_configuration(self.CONFIGURATION , None)
        #Set up variables
        self.SHOOTPHOTOSTORE = self.CONFIGURATION .photostore
        self.SHOOTDIRECTORY = os.path.join(self.SHOOTPHOTOSTORE,
                             datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        self.SCREEN_FONT = self.CONFIGURATION .Font
        self.SCREEN_FONT_SIZE = self.CONFIGURATION .Size
        self.SCREEN_FONT_COLOUR = self.CONFIGURATION .FontColour
        self.PHOTOSOUNDEFFECT = self.CONFIGURATION .shutterSound
        self.TWEET_TEXT = self.CONFIGURATION .TweetPhrase
        photoshoot = template.LoadPhotoShoot(self.CONFIGURATION .layout)
        self.debug_print_configuration(self.CONFIGURATION , photoshoot)
        PRINTERNAME = str(self.CONFIGURATION.PrinterName)
        self.PRINTER = getattr(importlib.import_module("libselfietorium.Printer"), "Printer")(PRINTERNAME)

        #Set Up Screens
        self.SCREEN_ATTRACT = open('Screens/Attract.svg').read()
        self.SCREEN_PREEN = open('Screens/Instructions2.svg').read()
        self.SCREEN_ERROR = open('Screens/Error.svg').read()
        self.SCREEN_TWITTER = open('Screens/Tweet.svg').read()
        self.SCREEN_TWITTER_IMAGE = open('Screens/TweetImage.svg').read()
        self.SCREEN_CONFIGURE = open('Screens/configure.svg').read()

        self.ERROR_FONT = self.CONFIGURATION.ErrorFont
        self.ERROR_FONT_SIZE = self.CONFIGURATION.ErrorFontSize
        self.ERROR_FONT_COLOUR = self.CONFIGURATION.ErrorFontColour
        self.CAMERA_MODULE = self.CONFIGURATION.CameraModule
        self.CAMERA_MODULE_FILE = self.CONFIGURATION .CameraFile
        self.FLASH_MODULE = self.CONFIGURATION.FlashModule
        self.FLASH_MODULE_FILE = self.CONFIGURATION.FlashFile

        self.ACCESS_TOKEN = self.CONFIGURATION.ACCESS_TOKEN
        self.ACCESS_SECRET = self.CONFIGURATION.ACCESS_SECRET
        self.CONSUMER_KEY = self.CONFIGURATION.CONSUMER_KEY
        self.CONSUMER_SECRET = self.CONFIGURATION.CONSUMER_SECRET
        self.TWITTERAUTHOR = self.CONFIGURATION.TweetAuthor
        self.HASHTAG = self.CONFIGURATION.TweetHashTag

        self.util = utilities.utilities()

        self.SocialMedia = SendTweet.selfie_Tweet(
            self.CONSUMER_KEY,
            self.CONSUMER_SECRET,
            self.ACCESS_TOKEN,
            self.ACCESS_SECRET,
            self.HASHTAG,
            self.TWITTERAUTHOR)

        self.CamerObject = importlib.import_module(self.CAMERA_MODULE )
        self.FlashObject = importlib.import_module(self.FLASH_MODULE)

        self.mymethod = getattr(importlib.import_module(self.CAMERA_MODULE ), self.CAMERA_MODULE_FILE)()
        self.flashmethod = getattr(importlib.import_module(self.FLASH_MODULE), self.FLASH_MODULE_FILE)()	

        self.state = "ATTRACT"
        pygame.init()
        pygame.mixer.init(48000, -16, 1, 1024)
        self.CAMERASOUND = pygame.mixer.Sound(self.PHOTOSOUNDEFFECT)
        print "WIDTH " + str(self.WIDTH)
        print "HEIGHT " + str(self.HEIGHT)
        print(pygame.display.Info())
        #size = pygame.display.list_modes()[0]
        #screen = pygame.display.set_mode(size,pg.FULLSCREEN)
        #pygame.display.set_mode((WIDTH,HEIGHT),0,16)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.mouse.set_visible(False)
        pygame.display.toggle_fullscreen()
        self.background = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))

        cbackground = pygame.Surface((self.WIDTH, self.HEIGHT))
        cbackground = cbackground.convert()
        cbackground.fill((200, 255, 255))


        self.c = pygame.time.Clock()
        while True:
            try:
                if "RPi.GPIO" in sys.modules:
                    #GPIO OVERRIDE
                    if not GPIO.input(12):
                        pygame.quit()
                        sys.exit()
                    if not GPIO.input(26):
                        if self.state == "ATTRACT" or self.state =="TWEET" :
                            self.state = "PREEN"

                for event in pygame.event.get():
                     
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()
                        elif event.key == pygame.K_p:
                            if self.state == "ATTRACT" or self.state =="TWEET" :
                                self.state = "PREEN"
                        elif event.key == pygame.K_c:
                            if self.state == "ATTRACT" or self.state =="TWEET" :
                                self.state = 'CONFIGURE'
                        elif event.key == pygame.K_s:
                            self.CAMERASOUND.play()
                        elif event.key == pygame.K_t:
                            self.state = "TWEET"
                        elif event.key == pygame.K_e:
                            #ErrorScreen(SCREEN_ERROR)
                            raise ValueError('A very specific bad thing happened')
                if self.state == "ATTRACT":
                    self.attract_screen(self.SCREEN_ATTRACT)
                if self.state == "TWEET":
                    self.twitter_latest(self.SCREEN_TWITTER,self.SCREEN_TWITTER_IMAGE)
                    self.state = "ATTRACT"
                if self.state == "CONFIGURE":
                    self.state = self.configure(photoshoot, self.SCREEN_CONFIGURE,self.CONFIGURATION.preenTime)
                    self.state = "ATTRACT"
                if self.state == "PREEN":
                    self.state = self.preen_screen(photoshoot, self.SCREEN_PREEN,
                                            self.CONFIGURATION.preenTime)
            except Exception as e:
                self.error_screen(self.SCREEN_ERROR, e)


            finally:
                self.c.tick(30)

def main_func():
    mc = mainclass()
    mc.main_loop()

if __name__ == '__main__':
    mc = mainclass()
    mc.main_loop()
