# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 20:05:34 2016

@author: kevinwo
"""

import media
import fresh_tomatoes as t

movies = []
m1 = media.Movie("Avatar",
                 "https://upload.wikimedia.org/wikipedia/en/b/b0/Avatar-Teaser-Poster.jpg",
                 "https://www.youtube.com/watch?v=Fq00mCqBMY8")
movies=[m1,m1,m1]
t.open_movies_page(movies)