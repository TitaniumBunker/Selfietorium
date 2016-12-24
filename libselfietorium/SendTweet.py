#!/usr/bin/python
#import twitter


class selfie_Tweet:

	def __init__(self):
	#	self.verified = False
	#	self.api = twitter.Api(
	#	consumer_key='0KfOMrcL9j89rz9Mo1DJTuKNw',
        #consumer_secret='rNoX4d7OE7FzcSh3i2x6JpNwzJDaqVkuqQW0ugug5C0XdXrrwQ',
        #access_token_key='709132628339859456-ffOEOiTzIKgFglEHeqTCznr9j4ueP8G',
        #access_token_secret='vI63eF1KkG29I8uJ4ZeFxkxzEOT29jVdRzFmHX7NRKXAD')
        #api.VerifyCredentials()
            pass

	def tweet(self,status):
		#if (self.verified):
			#api.PostUpdate(status)
		#	pass
		#else:
			print "posting to twitter " + status
		
	
	def tweetPhoto(self,status, media):
		print "posting media to twitter " + status + " > " + media
		#api.PostMedia(status,media)

# This is how you post a simple status update - like... Selfietorium booting up..
#api.PostUpdate('This is an eagle.')
#api.PostMedia('This is an Eagle','../Photo1.jpg')
