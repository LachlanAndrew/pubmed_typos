#!/usr/bin/python

import re
from unidecode import *
import sys
import pdb

abbreviations = {
  "a.c.",
  "d.c.",
  "e.g.",
  "e.p.",
  "e.s.r.",
  "e.u.",
  "i.e.",
  "i.v.",
  "i.p.",
  "i.u.",
  "i.ci.",
  "i.m.",
  "n.m.r.",
  "p.cent",
  "p.o.",
  "r.t."
  "s.c.",
  "s.e.",
  "e.p.p.",
  "e.p.p.s.",
  "m.e.p.p.",
  "m.e.p.p.s.",
  "U.S.",
  "Ph.D.",
  "Mr.",
  "Mrs.",
  "Dr.",
  "Prof.",
}

abbrev = {}
aa = [a for a in abbreviations]
for a in aa :
  b = a.split(".")
  if b and b[-1] == '' :
    del b[-1]
  for c in range(1,len(b)) :
    key = ".".join(b[0:c])
    if key not in abbrev :
      abbrev[key] = []
    abbrev[key].append(b[c])

# load typos
typos = {}
with open ("typos.txt", "r") as f :
  for line in f :
    line = line.split()
    typos[line[0][1:]] = line[0][0]

def parse (text) :
  """
  Parse text into words.
  Keep "." characters within words, like decimals and acronyms.
  Flag starts of sentences, so that we can tell if a capital is
  part of the work or just to mark the start of a sentence.
  """
  sentences = text.replace("--", "—").split(".")        # unicode em-dash
  words = [re.findall("[-\\w']+|[\\W]", s) for s in sentences]
  joined = []
  first_word = True
  for i, s in enumerate (words) :
    ## re-join hyphenated words here
    #if "-" in s :
    #  new_s = []
    #  for w in s :
    #    if len(new_s) > 1 and new_s[-1] == '-' and (re.match("\w+", new_s[-2])) and re.match ("\w+", w) :
    #      new_s[-2] = new_s[-2] + new_s[-1] + w
    #      del new_s[-1]
    #    else :
    #      new_s.append(w)
    #  s = new_s

    if not(s) :
      continue

    # Append to sentence list, or join this sentence to the previous
    join = False
    if joined :
      if len (joined[-1]) == 0:
        last = None
        join = True
      else :
        last = joined[-1][-1]
        if last in abbrev and (not abbrev[last]
                                or s[0] in abbrev[last]) :
          join = True
        if last[-1] in "0123456789" and s and s[0] and s[0][0] in "0123456789" :
          join = True

      #if joined[-1][0] == "(" :
      #  print (joined[-1])
      #  print ("***", s)
      #  pdb.set_trace ()

    if join :
      new_sentence = joined[-1][0:-1]
      not_punct = re.match("\w+", s[0])       # . was in acronym, so join it
      new_sentence.append((last + "." if last else "") + (s[0] if not_punct else ""))
      new_sentence.extend(s[1 if not_punct else 0 :])
      joined[-1] = new_sentence
    else :
      if (joined and s and len(s[0]) == 1 and unidecode(s[0]) in ")]}"
          and (len(s) == 1 or s[1] < "a" or s[1] > "z")) :
              # Closing bracket belongs with previous sentence
        joined[-1].append (s[0])
        del s[0]

      while (s and s[0] == " ") :
        del s[0]

      #if "The" in s and s[0] != "The" :
      #  print (s)
      #  pdb.set_trace ()

      if len(s) > 3 and s[0] == "(" and s[2] == ")" :
        joined.append(s[0:3])
        joined.append(s[3:])
      elif len(s) > 2 and unidecode(s[1]) == ")" :
        joined.append(s[0:2])
        joined.append(s[2:])
      else :
        joined.append(s)
        #if s[0] and s[0][0] >= "a" and s[0][0] <= "z" :
        #  print (line)
        #  print ("".join (joined[-2]))
        #  print (i, s)
        #  pdb.set_trace ()

    #if joined[-1][0] == "(" :
    #  print (joined[-1])
    #  print (s)
    #  pdb.set_trace ()

  return [[w for w in s if w != " "] for s in joined]

lexicon = {}
count_by_journal = {}

with open ("abstracts.txt", "r") as f :
  for line in f :
    parts = line.strip().split('"')
    if len (parts) < 3 :
      print ("Error", parts, file=sys.stderr)
      continue
    ID = parts[0] + '"' + parts[1] + '"'
    line = '"'.join(parts[2:])

    journal = " ".join(parts[0].split()[1:-1])
    if journal not in count_by_journal :
      # counts of: articles, articles with errors, sentences with errors
      count_by_journal[journal] = {"a": 0, "e": 0, "s": 0}
    count_by_journal[journal]["a"] += 1

    sentences = parse (line)

    if any ([any ([w in typos for w in s]) for s in sentences]) :
      for s in sentences :
        w = [w for w in s if w in typos]
        if w :
          print ("TYPO", w, ID, " ".join(s), file=sys.stderr)
          count_by_journal[journal]["s"] += 1

      count_by_journal[journal]["e"] += 1

      continue
    
    for s in sentences :
      first_word = True
      for i, w in enumerate(s) :
        if len(w) > 1 or re.match(r"[-\w']+", w) :
          if w not in lexicon :
            lexicon[w] = {"f": 0, "o": 0}
            #print(w, file=sys.stderr)

          #if w == "The" and not first_word :
          #  print (s)
          #  pdb.set_trace ()

          lexicon[w]["f" if first_word else "o"] += 1
          first_word = False

  print ("---")
  for j in sorted (count_by_journal, key = lambda w: -count_by_journal[w]["e"]/count_by_journal[w]["a"]) :
    c = count_by_journal[j]
    if c["e"] :
      print ("%4d %4d %4d" % (c["s"], c["e"], c["a"]), j)

  print ("---")
  for w in sorted(lexicon, key = lambda w: (-lexicon[w]["f"]-lexicon[w]["o"], w)) :
    print (w, lexicon[w]["o"], lexicon[w]["f"])
