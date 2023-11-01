#!/usr/bin/python

"""
Find most likely letter between a two-char prefix and a two-char suffix
"""

import pickle

max_context = 3

def add_context (char, ctxt, contexts) :
  if ctxt not in contexts :
    contexts[ctxt] = {char: 1}
  elif char not in contexts[ctxt] :
    contexts[ctxt][char] = 1
  else :
    contexts[ctxt][char] += 1

def add_subcontexts (char, ctxt, contexts) :
  for skip_pre in range(max_context) :
    for skip_post in range(max_context) :
      add_context (char, "*"*skip_pre +ctxt[skip_pre:len(ctxt)-skip_post]
                       + "*"*skip_post, contexts)

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
      word = "^"*max_context + line.lower().split()[0] + "$"*max_context

      for i in range (max_context, len(word)-max_context) :
        add_subcontexts (word[i], word[i-max_context:i] + word[i+1:i+1+max_context], contexts)

  normalize (contexts)

  save (contexts, outfile)

  return contexts

def likely_letters (model, thresh_sum, thresh_max) :
  mm = min (thresh_sum * model["sum"], thresh_max * model["max"])
  return [c for c in model if model[c] >= mm and len(c) == 1]

def missing_letters (ctxt, contexts) :
  neighbours = []
  if ctxt in contexts :
    neighbours.extend(likely_letters (contexts[ctxt], 0.01, 0.01))

  c = "*" + ctxt[1:]
  if c in contexts :
    neighbours.extend(likely_letters (contexts[c], 0.05, 0.1))

  c = ctxt[0:-1] + "*"
  if c in contexts :
    neighbours.extend(likely_letters (contexts[c], 0.05, 0.1))

  c = "*" + ctxt[1:-1] + "*"
  if ctxt in contexts :
    neighbours.extend(likely_letters (contexts[ctxt], 0.1, 0.1))

  c = "**" + ctxt[2:]
  if c in contexts :
    neighbours.extend(likely_letters (contexts[c], 0.25, 1))

  c = ctxt[0:-2] + "**"
  if c in contexts :
    neighbours.extend(likely_letters (contexts[c], 0.25, 1))

  c = "**" + ctxt[2:-1] + "*"
  if c in contexts :
    neighbours.extend(likely_letters (contexts[c], 0.5, 1))

  c = "*" + ctxt[1:-2] + "**"
  if c in contexts :
    neighbours.extend(likely_letters (contexts[c], 0.5, 1))

  c = "**" + ctxt[2:-2] + "**"
  if c in contexts :
    neighbours.extend(likely_letters (contexts[c], 0.75, 1))

  return neighbours

def neighbours (word : str, contexts) :
  ngbrs = []
  word = "^"*max_context + word.lower() + "$"*max_context

  for i in range (max_context, len(word) - max_context) :
    pref = word[max_context:i]

    # substitution errors
    suff = word[i+1:-max_context]
    ngbrs.extend ([pref + c + suff
                   for c in missing_letters(word[i-max_context:i]+word[i+1:i+max_context+1],
                                            contexts)])

    # deletion errors
    suff = word[i:-max_context]
    ngbrs.extend ([pref + c + suff
                   for c in missing_letters(word[i-max_context:i+max_context], contexts)])

  return ngbrs


if __name__ == "__main__" :
  pickle_file = "6tuple_model_med.pkl"
  try :
    contexts = load (pickle_file)
  except FileNotFoundError :
    contexts = build_contexts ("wordlist_nodup_nosim_med.txt", pickle_file)

  for word in ("anibodies",
               "animls"
              ) :
    for n in sorted (set (neighbours (word, contexts))) :
      print (n)
    print ()
