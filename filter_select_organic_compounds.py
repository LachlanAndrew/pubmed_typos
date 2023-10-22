#!/usr/bin/python

import sys

def exclude (word) :
  for stem in (
                "campyl",
                "ceylon",
                "chyli",
                "conchyl",
                "condyl",
                "cordyl",
                "cotyl",
                "crocodyl",
                "cylind",
                "dactyl",
                "gongyl",
                "gryllo",
                "pachyl",
                "sylvan",
                "phyl",
                "platyl",
                "psyll",
                "strongyl",
                "style",
                "styli",
                "stylo",
                "syll",
                "sylph",
                "sylv",
                "taylor",
                "xyl",
                "ylike",
                "zeylan",
              ) :
      if word.find(stem) >= 0 :
        return True

  return False

organics = {}

for line in sys.stdin :
  if line.find("yl") >= 0 :
    if len (line) >= 6 :
      line = line[0:-1]
      prefix = line[0:6]
      if prefix not in organics :
        organics[prefix] = []
      organics[prefix].append(line)

for i in organics :
  if len (organics[i]) > 5 :
    for name in organics[i] :
      if not exclude (name) :
        print (name)
