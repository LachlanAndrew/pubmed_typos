#!/usr/bin/python

import sys

omit_words = set()
if len (sys.argv) > 2 :
  with open (sys.argv[2], "r") as f :
    for line in f :
      omit_words.add(line)

lines = {}      # want an ordered set
for line in open (sys.argv[1], "r") :
  if line in omit_words :
    print ("*", line, end="")
  elif line not in lines or line == "\n":
    print (line, end="")
    lines[line] = None
