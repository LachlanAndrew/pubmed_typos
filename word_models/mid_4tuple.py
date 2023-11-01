#!/usr/bin/python

"""
Find most likely letter between a two-char prefix and a two-char suffix
"""

import pickle

def add_context (char, ctxt, contexts) :
  if ctxt not in contexts :
    contexts[ctxt] = {char: 1}
  elif char not in contexts[ctxt] :
    contexts[ctxt][char] = 1
  else :
    contexts[ctxt][char] += 1

def add_subcontexts (char, ctxt, contexts) :
  add_context (char, ctxt, contexts)
  add_context (char, "*" + ctxt[1:], contexts)
  add_context (char, ctxt[0:-1]+"*", contexts)
  add_context (char, "*" + ctxt[1:-1]+"*", contexts)

def normalize (contexts) :
  for i in contexts :
    con = contexts[i]
    try :
      con["sum"] = sum (con[c] for c in con)
    except :
      breakpoint ()
    con["max"] = max (con[c] for c in con)

def save (contexts, fname) :
  with open (fname, "wb") as f :
    pickle.dump (contexts,f)

current_context = ""
def load (fname) :
  if fname != current_context :
    with open (fname, "rb") as f :
      return pickle.load (f)

contexts = {}
def build_contexts (infile, outfile) :
  with open (infile, "r") as f :
    for line in f :
      word = "^^" + line.split()[0] + "$$"

      for i in range (2, len(word)-3) :
        add_subcontexts (word[i], word[i-2:i] + word[i+1:i+3], contexts)

  normalize (contexts)

  save (contexts, outfile)

def likely_letters (model, thresh_sum, thresh_max) :
  mm = min (thresh_sum * model["sum"], thresh_max * model["max"])
  return [c for c in model if model[c] >= mm and len(c) == 1]

def missing_letters (ctxt, contexts) :
  neighbours = []
  if ctxt in contexts :
    neighbours.extend(likely_letters (contexts[ctxt], 0.1, 0.1))

  c = "*" + ctxt[1:]
  if c in contexts :
    neighbours.extend(likely_letters (contexts[c], 0.5, 1))

  c = ctxt[0:-1] + "*"
  if c in contexts :
    neighbours.extend(likely_letters (contexts[c], 0.5, 1))

  c = "*" + ctxt[1:-1] + "*"
  if c in contexts :
    neighbours.extend(likely_letters (contexts[c], 0.75, 1))

  return neighbours

def neighbours (word : str, contexts) :
  ngbrs = []
  word = "^^" + word + "$$"

  for i in range (2, len(word) - 2) :
    pref = word[2:i]

    # substitution errors
    suff = word[i+1:-2]
    ngbrs.extend ([pref + c + suff
                   for c in missing_letters(word[i-2:i]+word[i+1:i+3],
                                            contexts)])

    # deletion errors
    suff = word[i:-2]
    ngbrs.extend ([pref + c + suff
                   for c in missing_letters(word[i-2:i+2], contexts)])

  return ngbrs


if __name__ == "__main__" :
  pickle_file = "4tuple_model.pkl"
  try :
    contexts = load (pickle_file)
  except FileNotFoundError :
    build_contexts ("wordlist_nodup_nosim_med.txt", pickle_file)

  for word in ("anibodies",
               "animls"
              ) :
    for n in sorted (set (neighbours (word))) :
      print (n)
    print ()
