import myjdapi
import time
import requests
from bs4 import BeautifulSoup

def getMovies(html):
    movies = []
    for items in html.select('item'):
        name = items.select('title')[0].text
        link = items.find('link').next_sibling
        hlink = '<a href="' + link.replace("\n", "").replace("\r","").replace("\t","") + '">' + name.replace(" ", ".") + '</a>'
        html_hlink = BeautifulSoup(hlink, 'html.parser')
        hlink = html_hlink.select('a')
        movies.append(hlink)

    return movies

def downloadLink(html, name):
    return False

def getURL():
    return "http://www.scnsrc.me/feed/rss/"

def getName():
    return "scnsrc"
