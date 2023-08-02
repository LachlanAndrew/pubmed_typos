#!/usr/bin/python

import sys
import tensorflow as tf
import numpy as np
import re

import pdb

file_suffix = "_1-1166"

features1 = {}
alternative = {}
word_counts = {}
with open ("words_classified%s.txt" % file_suffix, "r") as f :
  for line in f :
    line = line.split()
    word = line[0][1:]
    trust = line[0][0]
    ratio       = float(line[2])
    fixed_count = float(line[3])
    word_count  = float(line[4])

    features1[word] = (ratio, fixed_count, word_count)

    alternative[word] = line[1]
    word_counts[word] = word_count

features = {}
answers = {}
err_type_list = "X#*/+-S"
err_types = {}
with open ("words_neighbours%s.txt" % file_suffix, "r") as f :
  for line in f :
    line = line.split()
    word = line[0][1:]
    err_types[word] = line[-1]

    trust = line[0][0]
    uncertain  = float(line[-8])
    known_err  = float(line[-7])
    guess_err  = float(line[-6])
    underline  = float(line[-5])
    guess_true = float(line[-4])
    known_true = float(line[-3])
    only_opt   = float(line[-2])
    err_type = err_type_list.find(err_types[word])

    ratio, fixed_count, word_count = features1[word]

    inp = (np.log(max(ratio,1e-6)), np.log(max(fixed_count,1)), np.log(max(word_count,1)), uncertain, known_err, guess_err, underline, guess_true, known_true, only_opt, err_type)
    features[word] = inp
    answers[word] = trust

trust_symbols = {'-':0, '!':1, '=':1}
known = [w for w in answers if answers[w] in trust_symbols]

inputs = np.array([features[w] for w in known])
outputs = np.array([trust_symbols[answers[w]] for w in known])

model = tf.keras.Sequential([
  tf.keras.layers.Dense(units=1, activation='sigmoid', input_shape=(len(inputs[0]),))
])

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

#pdb.set_trace ()

tf.get_logger().setLevel("WARN")
model.fit(inputs, outputs, epochs=2)

predictions = model.predict(np.array([features[w] for w in features]))

word_score = [(w, 1-predictions[i][0]) for i, w in enumerate(features)]

"""
# Group space-separated words by their components to help a human
# distinguish typos from compound words (or compound words with typos).
for pattern in (# likely to be errors
                "after",
                "against",
                "air",
                "also",
                "and",
                "as",
                "assay",
                "at",
                "by",
                "each",
                "either",
                "end",
                "every",
                "except",
                "for",
                "formation",
                "from",
                "half",
                "has",
                "here",
                "of",
                "off",
                "only",
                "order",
                "other",
                "result"
                "showed",
                "study",
                "test",
                "than",
                "that",
                "the",
                "then",
                "there",
                "these",
                "this",
                "those",
                "to",
                "together",
                "use"
                "used"
                "was",
                "were",
                "with",

                # Legitimate prefix/suffix
                "form",
                "forming",
                "like",
                "wide",
                "pre",
                "post",
                "therapy",
                "infra",
                "hyper",
                "hypo",
                "ante",
                "anti",
                "non",
                "un",
                "de",
                "re",
                "co",
                "under",
                "over",
                "ward",
                "endo",
                "auto",
                "equi",
                "meta",
                "virus",

                "uni",
                "mono",
                "bi",
                "bis",
                "di",
                "tri",
                "tetra",
                "penta",
                "hexa",

                "sub",
                "super",
                "supra",
                "extra",
                "intra",
                "inter",
                "trans",
                "retro",
                "iso",
                "para",
                "gram",
                "graph.*",
                "nano",
                "pico",
                "micro",
                "macro",
                "mega",
                "mid",
                "semi",
                "multi",
                "poly"
                "oligo",
                "ultra",
                "pseudo",
                "quasi",
                "exo",
                "endo",
                "peri",
                "dis",
                "homo",
                "hetero",
                "mal",

                "electro",
                "magneto",
                "radio",
                "video",
                "photo",

                "cardio",
                "immuno",
                "neuro",
                "cyto",
                "heme",
                "psycho",
                "socio",

                "less",
                "fold",
                "able",
                "ability",

                "alkyl",
                "acetyl",
                "amino",
                "oxy",
                "deoxy",
                "ol",
                "ase",
                "methyl",
                "ethyl",
                "iodo",
                "nitro",
                "aryl",
                "hydroxyl",
                "amine",
                "phenyl",
                "ester",
                "chloro",
                ".*oxy.*",
                ".*fluor.*",
                ".*amine.*",
                ".*yl",

                "ic",
                "al",
                "ally",
                "ly",
                "ed",
                "es",
                "us",
                "ex",
                "dia",
                "ism",
                "id",
                "ia",

                # Could be either
                "self", # hyphenated?
                "an",
                "if",
                "in",
                "is",
                "it",
                "nor",
                "on",
                "or"
                "ions?",
                ) :
  for p in ("^.*_"+pattern+"$", "^"+pattern+"_.*$") :
      matches = []
      non_matches = []

      for w in word_score :
        #if "_" in alternative[w[0]] : pdb.set_trace ()
        if re.match(p, alternative[w[0]]) :
          matches.append(w)
        else :
          non_matches.append(w)

      word_score = non_matches

      printed = False
      for w in sorted (matches, key = lambda x : -x[1]) :
        print (answers[w[0]]+w[0], alternative[w[0]], w[1], err_types[w[0]])
        printed = True
      if printed :
        print ()

for w in sorted (word_score, key = lambda x : -x[1]) :
  print (answers[w[0]]+w[0], alternative[w[0]], w[1], err_types[w[0]])

print ("\n----------\n")
"""

has_space = [w for w in word_score if "_" in alternative[w[0]]]
no_space = [w for w in word_score if "_" not in alternative[w[0]]]
word_score = None

for w in sorted (no_space, key = lambda x : -x[1]) :
  print (answers[w[0]]+w[0], alternative[w[0]], w[1], word_counts[w[0]], err_types[w[0]])

# Order by pairs with most common word, then by more common word first,
# then by the frequency of the less common word, then by error score,
# then alphabetically
split_scores = {}
for w in has_space :
  ws = alternative[w[0]].split("_")
  count0 = word_counts[ws[0]] if ws[0] in word_counts else 0
  count1 = word_counts[ws[1]] if ws[1] in word_counts else 0
  split_scores[w[0]] = (-min(count0, count1), 0 if count0 > count1 else 1, -max(count0, count1), -w[1], w)

for w in sorted (has_space, key = lambda w : split_scores[w[0]]) :
  print (answers[w[0]]+w[0], alternative[w[0]], w[1], word_counts[w[0]], err_types[w[0]])

exit()
