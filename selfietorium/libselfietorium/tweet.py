#!/usr/bin/python
# -*- coding: utf-8 -*-
import tweepy
 
# Consumer keys and access tokens, used for OAuth
consumer_key = 'CcXp9EEIYwlkxfcKPIIMxNA72'
consumer_secret = 'YXdChtEWBm06zZnLxbSHlIr2P2d6pRNrybmXopRpXtIE8zlEL8'
access_token = '709132628339859456-yeTDqltA5XLlex9zF7YlF5lwSWliA6k'
access_token_secret = 'UmILA5o1h0czluBmVzgsuBUjyta11BSCEVTP0j3tixQR7'
 
# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
 
# Creation of the actual interface, using authentication
api = tweepy.API(auth)
 
# Sample method, used to update a status
api.update_status('Hello Python Central!')