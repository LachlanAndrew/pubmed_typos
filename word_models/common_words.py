#!/usr/bin/python3

import sys

import pdb

import read_merged
import unidecode

if len (sys.argv) > 1 :
  langs = sys.argv[1:]
else :
  langs =["en", "cy", "da", "de", "es", "fr", "in", "it", "jp",
          "kr", "nl", "pl", "ar", "hi", "id", "ma", "md", "tl", "slv", "zh"] 

languages = langs
languages.extend (["maual_"+a for a in langs])

languages = {a:"words_"+a+".txt" for a in languages }

priority = {lang: ["oth"] for lang in langs}
if "oth" in priority :
  del priority["oth"]
if "pl" in priority :
  priority["pl"].append("slv")
if "en" in priority :
  priority["en"].append("md")

#languages.update({"hi":"words_hawaiian.txt",
#                  "id":"words_indonesian.txt",
#                  "ma":"words_maori.txt",
#                  "md":"words_medical.txt",
#                  "tl":"words_tagalog.txt"})

src = read_merged.read_merged(languages, ignore_missing=True) #, unidecode.unidecode_expect_ascii)

handles = {a:open("wordlist_nodup_"+a+".txt", "w") for a in src.files}

while True :
  word, lang = src.next(tell_origin=True, merge_duplicates=True) 
  if word == None :
    break

  word = word.rstrip()
  lang1 = {a for a in lang}

  # ignore secondary entry if one language has priority over another
  any_priority = {a for a in lang1 if a in priority }
  #if len (lang1) == 2 and "oth" in lang1 : pdb.set_trace ()
  if len(any_priority) == 1 :
    lang2 = lang1.difference (any_priority)
    if all ([a in priority[b] for a in lang2 for b in any_priority]) :
      lang = [b for b in any_priority]
      lang1 = lang

  if len (lang1) > 1 :   # word in multiple dictionaries
    print (lang, word)
  else :
    print (word, file=handles[lang[0]])
