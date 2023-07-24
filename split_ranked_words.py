#!/usr/bin/python

import sys

import pdb

non_prefix = {
  "ac",
  "al",
  "as",
  "be",
  "be",
  "ca",
  "cu",
  "cy",
  "du",
  "fo",
  "he",
  "how",
  "is",
  "la",
  "le",
  "me",
  "met",
  "mo",
  "mu",
  "no",
  "ob",
  "pa",
  "po",
  "ser",
  "se",
  "so",
  "th",
  "the",
  "to",
  "va",
  "vi",
}

non_suffix = {
  "ions",
}

# spell check procedure:
# Start with domain-specific text, parsed to words
# Strip known English words
# Train models on English words and domain-specific words
# Maximum likelihood classify words as English or domain-specific
# 
# Identify a few errors
# Weight sources by error rate
# Split words into common-prefix + common-suffix, or sequence of components
# Rate component by [frequency / (expected frequency from 0-order model)]
#
# hyphenation
# count times that joined word is more common than either component
#   and joined word fits in context.

def split_word (word, rank, trusted = {}, pref = {}, suff = {}, stats = None, non_prefix = {}, non_suffix = {}) :
  best_f = None
  for i in range (2, len(word)-3) :
    w1 = word[0:i] 
    w2 = word[i:]
    #if word == "zymotaxonomical" : pdb.set_trace()
    if ((w1 in pref or w2 in suff or (w1 in trusted and w2 in trusted))
        and not w1 in non_prefix and not w2 in non_suffix) :
      f1 = 2+(pref[w1] if w1 in pref else (rank[w1] if w1 in rank else 3*len (rank)))
      f2 = 2+(suff[w2] if w2 in suff else (rank[w2] if w2 in rank else 3*len (rank)))
      cost = f1*f2 / min(len(w1), len(w1))**4
      #if word == "control" : print (w1, w2, f1, f2, cost); pdb.set_trace ()
      if (not best_f or cost < best_f) :
        best_i = i
        best_f = cost

  if best_f :
    if stats :
      stats.f1 = rank[w1]
      stats.f2 = rank[w2]
      stats.fw = rank[word]
    return [word[0:best_i], word[best_i:]]
  else :
    return [word]


def count_dict (dictionary, key) :
  if not key in dictionary :
    dictionary[key] = 0
  dictionary[key] += 1

def process (word, rank, lexicon, learning_pref = None, learning_suff = None, known_pref={}, known_suff={}, display = False, non_prefix = {}, non_suffix = {}) :
  #if word.startswith("than"): pdb.set_trace()
  w = split_word(word, rank, lexicon, pref = known_pref, suff=known_suff, non_prefix = non_prefix, non_suffix = non_suffix)
  if len (w) > 1 :
    br = "_".join(w) 
    #breaks[word] = br
    if display :
      print (br, display)
    if (learning_pref != None) :
      count_dict(learning_pref, w[0])
    if (learning_suff != None) :
      count_dict(learning_suff, w[1])
  elif display :
    print (display, file=sys.stderr)
    pass

################################################################################

if len(sys.argv) < 2 :
  print ("usage:", sys.argv[0], "<word_file> [number_trusted]")
  exit(1)
filename = sys.argv[1]

if len(sys.argv) > 2 :
  trusted = int(sys.argv[2])
else :
  trusted = 20000

count = 0
trusted_words = {}
prefixes = {}
suffixes = {}
#breaks = {}

with open (filename, "r") as f :
  for line in f :
    line = line.split()[0].lower()
    if count <= trusted :
      trusted_words[line] = count
      if count == trusted :
        for word in trusted_words :
          process (word, rank=trusted_words, lexicon=trusted_words, learning_pref=prefixes, learning_suff=suffixes, non_prefix = non_prefix, non_suffix = non_suffix)
    else :
      process (line, rank=trusted_words, lexicon=trusted_words, learning_pref=prefixes, learning_suff=suffixes, non_prefix = non_prefix, non_suffix = non_suffix)
    count += 1

iterations = 4
for it in range(iterations) :
  if "zymo" in prefixes :
    print ("zymo", prefixes["zymo"], 2*len("zymo") + prefixes["zymo"] > 20)
  else :
    print ("no zymo")
  known_prefixes = {w:i for i,w in enumerate(sorted(prefixes, key = lambda w: -2*len(w) - prefixes[w])) if 2*len(w) + prefixes[w] > 20 and ('a' in w or 'e' in w or 'i' in w or 'o' in w or 'u' in w or 'y' in w)}
  #known_prefixes["dis"] = known_prefixes["di"]/2
  if "zymo" in known_prefixes :
    print ("zymo", known_prefixes["zymo"])
  else :
    print ("no zymo")

  known_suffixes = {w:i for i,w in enumerate(sorted(suffixes, key = lambda w: -5*len(w) - suffixes[w])) if 5*len(w) + suffixes[w] > 50}

  prefixes = {}
  suffixes = {}
  with open (filename, "r") as f :
    for line in f :
      word = line.split()[0].lower()
      #if word == "zymotaxonomical" : pdb.set_trace ()
      process (word, rank=trusted_words, lexicon=trusted_words, learning_pref=prefixes, learning_suff=suffixes, known_pref=known_prefixes, known_suff=known_suffixes, non_prefix = non_prefix, non_suffix = non_suffix, display=line.strip() if (it == iterations-1) else False)

  print ("Done iter", it)
  if "zymo" in prefixes :
    print ("zymo", prefixes["zymo"], 2*len("zymo") + prefixes["zymo"] > 20)
  else :
    print ("no zymo")
  #pdb.set_trace()


# print prefixes and suffixes ordered by frequency
with open ("pref_suff.py", "w") as f :
  print ("known_prefixes = {", file = f)
  for word in sorted (prefixes, key = lambda w: (len(w), -prefixes[w], w)) :
    print (str({word:prefixes[word]})[1:-1]+",", file = f)
  print ("}\n", file=f)

  print ("known_suffixes = {", file = f)
  for word in sorted (suffixes, key = lambda w: (len(w), -suffixes[w], w)) :
    print (str({word:suffixes[word]})[1:-1]+",", file = f)
  print ("}\n", file=f)
