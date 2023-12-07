#!/usr/bin/python

import sys

use_4tuple = False

if use_4tuple :
  import mid_4tuple as tuple_pred
else :
  import mid_6tuple as tuple_pred
import guess_lang

def edit_distance_1(word: str) :
  """Compute all strings that are one edit away from `word`
     allowing only transpositions and deletions

  Args:
      word (str): The word for which to calculate the edit distance
  Returns:
      set: The set of strings that are edit distance one from the provided word"""
  tmp_word = word.lower()
  splits = [(tmp_word[:i], tmp_word[i:]) for i in range(len(tmp_word) + 1)]
  deletes = [L + R[1:] for L, R in splits if R]
  transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]

  # If a word has a double, people often double the wrong letter
  # Make that "edit distance 1"
  swap_dub = []
  for i in [j for j in range(len(tmp_word)-1) if tmp_word[j]==tmp_word[j+1]] :
    w = tmp_word[:i]+tmp_word[i+1:]
    swap_dub.extend ([ L + R[0] + R
                      for L, R in [(w[:i],w[i:]) for i in range(len(w))]])

  # Transpose letters separated by one
  trans2 = [L + R[3::-1] + R[3:] for L, R in splits if len(R) > 2]

  return set(deletes + transposes + swap_dub + trans2)

models = guess_lang.init(["med"])
contexts = tuple_pred.load (("4" if use_4tuple else "6") + "tuple_model_%s.pkl" % "med")
def init (lex) :
  contexts = tuple_pred.load (("4" if use_4tuple else "6") + "tuple_model_%s.pkl" % "med")
  models = guess_lang.init([lex])       # Why local?

def similar_words (word: str) :
  # Identify most likely lexicon
  # assume all medical

  # generate all transposition and insertion errors (i.e., deletions from this)
  ngbrs = edit_distance_1 (word)

  # For each position, use new 4-tuple model to generate most likely change or deletion
  ngbrs1 = tuple_pred.neighbours (word, contexts)
  ngbrs.update (set (ngbrs1))

  # Evaluate probability of each option
  log_prob = {w: guess_lang.word_prob(w, models["med"]) for w in ngbrs}

  best = sorted (ngbrs, key= lambda w : -log_prob[w])

  return best


  thresh = 1.2 * log_prob[best[0]]       # 2* not 0.5* because log probs are negative
  #print (str({w:log_prob[w] for w in best}).replace(',', '\n'))
  return [b for b in best if log_prob[b] >= thresh]

def load_known () :
  known = {}
  with open ("tmp_neighbours1.txt", "r") as f:
    new_word = True
    for line in f:
      line = line.rstrip ().split ()
      if line == [] :
        new_word = True
      else :
        new_word = False
        if len (line) == 1 :
          curr_word = line[0]
        else :
          if line[0][0] in "*=" :
            if curr_word in known :
              known[curr_word] += "/" + line[0][1:]
            else :
              known[curr_word] = line[0][1:]
          elif line[0][0] == "'" :
            known[line[0][1:-2]] = line[1][2:-2]

  return known

guesses = {}
guess_counts = {}

if __name__ == "__main__" :
  init ("med")
  for line in sys.stdin :
    w = line.lstrip("#").strip()
    guesses[w] = similar_words(w)
    for g in guesses[w] :
      if g in guess_counts :
        guess_counts[g] += 1
      else :
        guess_counts[g] = 1

  known = load_known ()

  for w in guesses :
    if w not in known :
      order = [g for g in guesses[w]]
      print (w)
      showed_known = False
      k = known[w] if w in known else None
      for i, g in enumerate (sorted([(-guess_counts[order[i]], i) for i in range(len(order))])) :
        gg = order[g[1]]
        if gg == k :
          print ("*", end="")
          showed_known = True
        print (gg, guess_counts[gg],
               " " + chr(min(ord('A')+i,126)) if gg == w else "")
      if k and not showed_known :
        print ('=' + k, 0)
      print ()

  for w in guesses :
    if w in known :
      print (str({w:(known[w], "")})[1:-1] + ",")

  #print (similar_words ("animls"))
  #print (similar_words ("chromotographs"))
  #print (similar_words ("chylomicroms"))
  #print (similar_words ("cortiocotropin"))
  #print (similar_words ("cortiocotropin"))
  #print (similar_words ("corticortropin"))

