#!/usr/bin/python

import sys
import re

first_word = re.compile ("^[^a-zA-Z]*([a-zA-Z]+)")

def first_ascii_letters (line) :
  m = first_word.search(line)
  if m :
    return m.group(1)
  else :
    return line

line_key = lambda x: x
while len (sys.argv) > 1 :
  if sys.argv[1].startswith('-') :
    if sys.argv[1] == "--first" :
      line_key = first_ascii_letters
      del sys.argv[1]

    if sys.argv[1] == "--help" :
      print (f"Usage: {sys.argv[0]} [--first] [--help] [infile [outfile]]",
             file=sys.stderr)

  else :
    break


omit_words = set()
if len (sys.argv) > 2 :
  with open (sys.argv[2], "r") as f :
    for line in f :
      omit_words.add(line_key(line))

lines = {}      # want an ordered set
if len (sys.argv) > 1 :
  for line in open (sys.argv[1], "r") :
    k = line_key(line)
    if k in omit_words :
      print ("*", line, end="")
    elif line not in lines or line == "\n":
      print (line, end="")
      lines[k] = None

else :
  for line in sys.stdin :
    k = line_key(line)
    if k in omit_words :
      pass
    elif line not in lines or line == "\n":
      print (line, end="")
      lines[k] = None
