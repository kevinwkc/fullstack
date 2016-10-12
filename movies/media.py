# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 19:27:12 2016
You will write server-side code to store a list of your favorite movies, including box art imagery and a movie trailer URL. You will then use your code to generate a static web page allowing visitors to browse their movies and watch the trailers.
@author: kevinwo
"""

class Movies(object):
    def __init__(self):
        self.list = []
    def __iter__(self):
        return iter(self.list)
    def add(self, movie):
        self.list+=movie

class Movie(object):
  
    def __init__(self, title,poster_image_url,trailer_youtube_url):
        self.title=title
        self.poster_image_url=poster_image_url
        self.trailer_youtube_url=trailer_youtube_url