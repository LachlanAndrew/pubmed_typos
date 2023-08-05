#!/usr/bin/python

import sys

import pdb

sys.path.insert(0, "../pyspellchecker")
from spellchecker import SpellChecker

from known_errs import known_errs

file_suffix = "_1-1166"

prefix = {"al", "pi", "vas",}
suffix = {"al", "ion", "us", "ed", "er", "es", "ia", "ic", "id", "ie", "la", "le", "na", "ne", "ng", "ns", "nt", "ol", "re", "ri", "ro", "rs", "ta",}

spell = SpellChecker(language = "en", distance=1, always=True)
spell_jargon = SpellChecker(language = "en", distance=1, always=True)

# Take a candidate replacement word, and eliminate quirks
# - don't split off a one-letter "word" unless that word is "a"; drop the letter
# - don't return values ending with "'s"; drop the s.
def tidy_candidate (word: str) :
  w = word.split()
  if len (w) == 2 :
    if len(w[0]) == 1 and w[0] != "a" :
      return w[1]
    elif len(w[1]) == 1 and w[1] != "a" :
      return w[0]

  if word.endswith("'s") :
    word = word[:-2]

  return word

checked_words = set()
with open ("checked_words.txt", "r") as f :
  for line in f :
    word = line.strip()
    checked_words.add(word)
    #if word in known_errs :
    #  print ("~", word)


trusted_freq = 122
trusted_freq = None

# Estimate how many occurrences need to occur for us to trust a word to
# be "real"
# (Not yet working.)
if trusted_freq == None :
  freq_quantiles = []
  prev_freq = 1e30
  count = 1
  with open ("words_ranked%s.txt" % file_suffix, "r") as f :
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
  #pdb.set_trace ()

  # Override untrusted calculations
  trusted_freq = 122

itr = 1
jargon_counts = {}
known_counts = {}
with open ("words_ranked%s.txt" % file_suffix, "r") as f,         \
     open ("words_base%s.txt"   % file_suffix, "w") as base,        \
     open ("words_jargon%s.txt" % file_suffix, "w") as jargon :
  for line in f :
    line = line.split()
    my_freq = int(line[1]) + int(line[2])
    word = line[0]

    if spell.known ([word]) :
      print (" ".join(line), file=base)
      known_counts [word] = my_freq
      #elif itr < trusted_count :
    elif my_freq >= trusted_freq:
      print (" ".join(line), file=jargon)
      jargon_counts [word] = my_freq

    itr += 1

spell_jargon.word_frequency.load_json(jargon_counts)

# Train recognizers for base and jargon
# (Also recognizers for base-errors and jargon-errors?)

# Look for probably typos, joined words, or words built of pairs of trusted words
# ! for known valid
# + for guessed valid
# _ for joined
# ? for undecided
# * for guessed error
# - for known error

with open ("words_ranked%s.txt"    % file_suffix, "r") as f,            \
     open ("words_classified%s.txt" % file_suffix, "w") as outfile :
  for line in f :
    line = line.split()
    my_freq = int(line[1]) + int(line[2])
    word = line[0]

    change_type = '?'           # unsure if error or related word

    if word in known_errs :
      if word in checked_words :
        print ("e" if word == known_errs[word]+"e" else "~",
               word, known_errs[word])
        sys.stdout.flush()

      candidate = known_errs[word]
      change_type = '-'         # known error
    else :
      candidates = spell_jargon.ranked_candidates(word, keep_scores=True)

      candidate, score, freq, sim, reason = candidates[0]
      ## Prefer to drop a letter than split one letter off as a word, except "a"
      c = tidy_candidate (candidate)

      known = word in checked_words # spell.known([word])
      
      if (my_freq > trusted_freq or known) :
        if len(word) > 1 :
          for i in range (len (candidates)) :
            word = word.lower ()
            candidate, score, freq, sim, reason = candidates[i]

            # TODO: Avoid repetition with the above code
            c = tidy_candidate (candidate)

            if freq > trusted_freq and 10*freq > my_freq:
              candidate = candidate.lower()

              if (not " " in candidate and len(candidate)>1
                  and word != candidate and candidate not in known_errs
                  and word != candidate+'s' and word != candidate+'d'
                  and word+'s' != candidate and word+'d' != candidate
                 ):
                change_type = "!" if known else "+"
                #print (word, candidate, freq/my_freq, freq,
                #       line[1], line[2], my_freq, file=valid_pairs)
                #printed = True
                break

          # If none looks good, revert to the first
          if change_type == "?" :
            candidate, score, freq, sim, reason = candidates[0]
            if candidate == word and len(candidates) > 1 :
              candidate, score, freq, sim, reason = candidates[1]

            if freq > trusted_freq and 10*freq > my_freq:
              candidate = candidate.lower()
              if candidate != word.lower() and candidate not in known_errs :
                # TODO: Avoid repetition with the above code
                c = tidy_candidate (candidate)
                change_type = "!" if known else "+"

          if change_type == "?" :
            candidate = word+"/"
            change_type = "="

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
      if (change_type == '?' and freq > 100 * my_freq
                      and word.lower() != candidate.lower()
                      and len (candidate) >= 4) :
        # TODO: capitalize (or bold?) differences between word and candidate
        for i in range (len (candidates)) :
          word = word.lower ()
          candidate, score, freq, sim, reason = candidates[i]

          # TODO: Avoid repetition with the above code
          c = tidy_candidate (candidate)

          if " " in candidate :
            cand_words = c.split()
            if word.lower() == "".join(cand_words).lower() :
              candidate = candidate.replace (" ", "_")
              if (cand_words[0] in prefix or cand_words[1] in suffix
                  or (len(cand_words[0]) <= 2 and cand_words[0] in known_counts and known_counts[cand_words[0]] > 10000)
                  or (len(cand_words[1]) <= 2 and cand_words[1] in known_counts and known_counts[cand_words[1]] > 10000)
                  or len(cand_words[0]) == 1 or len(cand_words[1]) == 1) :
                # not missed space; maybe a misspelling or space-replacement
                #print (word, candidate.replace(" ", "_"), freq / my_freq, freq, line[1], line[2], my_freq, file=errs)

                # try a different correction
                continue
              else :
                # separate check for merged words.
                #print (word, candidate.replace(" ", "_"),
                #       freq / my_freq, freq, line[1], line[2], my_freq, file=joined)
                change_type = '_'  # joined words
                #change_type = '*'  # (joined words are errors)
                break
            else :
              candidate = candidate.replace (" ", ":")
              #print (word, candidate.replace(" ", ":"), freq / my_freq, freq, line[1], line[2], my_freq, file=errs)
              change_type = '*'    # likely error
              break

          else :
            #print (word, candidate, freq / my_freq, freq, line[1], line[2], my_freq, file=errs)
            change_type = '*'    # likely error
            break

        # If all options failed (bad suffix/prefix), revert to the first
        if change_type == '?' :
          candidate, score, freq, sim, reason = candidates[i]
          candidate = tidy_candidate(candidate).replace (" ", "_")
          change_type = "*"

    if word != candidate :
      print (change_type+word, candidate.replace(" ", "_"),
             freq / my_freq, freq, line[1], line[2], my_freq, file = outfile)
