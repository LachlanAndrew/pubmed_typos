#!/usr/bin/python

import sys

sys.path.insert(0, "../pyspellchecker")
from spellchecker import SpellChecker

prefix = {"al", "pi", "vas",}
suffix = {"al", "ion", "us"}

spell = SpellChecker(language = "en", distance=1, always=True)

trusted_freq = 122
trusted_freq = None

if trusted_freq == None :
  freq_quantiles = []
  prev_freq = 1e30
  count = 1
  with open ("words_only.txt", "r") as f :
    for line in f :
      line = line.split()
      my_freq = int(line[1]) + int(line[2])
      word = line[0]

      if my_freq < prev_freq :
        freq_quantiles.append((count, my_freq))
        prev_freq = my_freq

      count += 1

  if not freq_quantiles :
    printf ("No known words", file=sys.stderr)
    exit(1)
  trusted_count, trusted_freq = min ([entry for entry in freq_quantiles
                                            if entry[0]*entry[1] > count],
                                     key = lambda x: x[1])

count = 1
jargon_counts = {}
with open ("words_only.txt", "r") as f            \
     open ("words_base.txt", "w") as base,        \
     open ("words_jargon.txt", "w") as jargon :
  for line in f :
    line = line.split()
    my_freq = int(line[1]) + int(line[2])
    word = line[0]

    if spell.known (word) :
      print (" ".join(line), file=base)
    elif count < trusted_count
      print (" ".join(line), file=jargon)
      jargon_counts [word] = my_freq

    count += 1

spell.load_json(jargon_counts)

# Train recognizers for base and jargon
# (Also recognizers for base-errors and jargon-errors?)

# Look for probably typos, joined words, or words built of pairs of trusted words
with open ("words_ranked.txt", "r") as f,             \
     open ("words_joined.txt", "w") as joined,        \
     open ("words_pairs.txt", "w") as valid_pairs :
  for line in f :
    line = line.split()
    my_freq = int(line[1]) + int(line[2])
    word = line[0]
    candidates = spell.ranked_candidates(word, keep_scores=True)
    candidate, score, freq, sim, reason = candidates[0]
    if my_freq > trusted_freq :
      if len(word) > 1 :
        for i in range (len (candidates)) :
          word = word.lower ()
          candidate, score, freq, sim, reason = candidates[i]
          if freq > trusted_freq and 100*freq > my_freq:
            candidate = candidate.lower()
            if (not " " in candidate and len(candidate)>1 and word != candidate
                and word != candidate+'s' and word != candidate+'d'
                and word+'s' != candidate and word+'d' != candidate) :
              print (word, candidate, freq/my_freq, freq,
                     line[1], line[2], my_freq, file=valid_pairs)
              break
      #if ((" " in candidate or len (word) == 1 or len(candidate) == 1
      #    or word.lower() == candidate.lower()
      #    or word == candidate + 'd' or word == candidate + 's'
      #    or word + 'd' == candidate or word + 's' == candidate)
      #    and len(candidates) > 1) :
      #  candidate, score, freq, sim, reason = candidates[1]
      #if (not " " in candidate and len (word) > 1 and len(candidate) > 1
      #    and word.lower() != candidate.lower()) :
      #  print (word, candidate,
      #         freq/my_freq, freq, line[1], line[2], my_freq, file=valid_pairs)
    elif (freq > 100 * my_freq and word.lower() != candidate.lower()) :
      # TODO: capitalize (or bold?) differences between word and candidate
      if " " in candidate :
        cand_words = candidate.split()
        if word.lower() == "".join(cand_words).lower() :
          if (cand_words[0] in prefix or cand_words[1] in suffix
              or len(cand_words[0]) == 1 or len(cand_words[1]) == 1) :
            # not missed space; maybe a misspelling or space-replacement
            print (word, candidate.replace(" ", "_"), freq / my_freq, freq, line[1], line[2], my_freq)
          else :
            # separate check for merged words.
            print (word, candidate.replace(" ", "_"),
                   freq / my_freq, freq, line[1], line[2], my_freq, file=joined)
        else :
          print (word, candidate.replace(" ", ":"), freq / my_freq, freq, line[1], line[2], my_freq)
      else :
        print (word, candidate, freq / my_freq, freq, line[1], line[2], my_freq)
