#!/usr/bin/env python
"""
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""
import urllib2

import scrapy
import shlex

from BeautifulSoup import BeautifulSoup
from scrapy.http import Request

import uuid
import re
import json
from HTMLParser import HTMLParser
import os, sys
import logging

import Queue


class MidiSpider(scrapy.Spider):
    name = "midi"
    allowed_domains = ["midiworld.com"]
    reverse_lookup = {}
    url_lookup = {}
    start_urls = []

    artists = {}
    queue = None
    urls =  None
    out = "out"


    def __init__(self):
        url = "http://www.midiworld.com/files/{}/all/"

        self.urls = open('urls.txt', 'w')
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


        self.queue = Queue.Queue()

        for i in shlex.split("a b c d e f g h i j k l m n o p q r s t u v w x y z"):
        # for i in shlex.split("a"):
            updated_url = url.format(i)
            # self.queue.put(updated_url)
            # self.start_urls.append(updated_url)
            self.start_urls.append(updated_url)
            self.reverse_lookup[i] = updated_url
            # self.url_lookup[updated_url] = i
            self.artists[i] = {}

    def __del__(self):
        self.urls.close()

    def parse_author(self, author, request):
        import os

        author_path = os.path.join(self.out, author)
        if not os.path.exists(author_path):
            os.mkdir(author_path)
        page = urllib2.urlopen(request.url)
        soup = BeautifulSoup(page.read())


        # downloads = soup.findAll("li")
        downloads = soup.find("div", {"id": "page"}).find("ul").findAll("li")
        for item in downloads:
            child = item.next
            song_name = child.text
            url = item.find("a").attrs[0][1]
            logging.info("Download: {} for author: {}".format(url), author)
            output = self.build_url(author, song_name)
            f = urllib2.urlopen(url)
            data = f.read()
            output = open(output, 'wb')
            output.write(data)
            output.close()


        print('process author: {}'.format(author))

    def build_url(self, author, song):
        return os.path.join(self.out, author, song + ".midi")


    def parse(self, response):
        if response.url in self.url_lookup:
            author = self.url_lookup[response.url]
            self.parse_author(author, response)
            return

        body = response.xpath("//body").extract()[0]

        bodySoup = BeautifulSoup(body)
        authors = bodySoup.find("div", {"id": "page"}).find("table").findAll("a")
        for author in authors:
            url = author.attrs[0][1]
            # self.urls.write(author.text + ":" + url + "\n");
            self.queue.put(url)
            self.artists [author.text] = url
            self.url_lookup[url] = author.text
            self.parse(Request(url, dont_filter=True))

        # next_page = bodySoup.find("a", {"class": "nomark"})
        # if next_page is not None:
        #     self.parse(Request(url, dont_filter=True))


