#!/usr/bin/python

import sys
import tensorflow as tf
import numpy as np
import re

import pdb

file_suffix = "_caps_1-1166"

if len(argv) > 1 :
  file_suffix = argv[1]

features1 = {}
alternative = {}
word_counts = {}
with open ("words_classified%s.txt" % file_suffix, "r") as f :
  for line in f :
    line = line.split()
    if not line :
     continue
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
cause_list = "OTS?"     # OCR, typing, spelling, unknown
err_type_list = "X#*/+-S"
err_types = {}
with open ("words_neighbours%s.txt" % file_suffix, "r") as f :
  for line in f :
    line = line.split()
    word = line[0][1:]
    try :
      err_types[word] = line[-2][1]
    except :
      breakpoint ()

    trust = line[0][0]
    uncertain  = float(line[-12])
    known_err  = float(line[-11])
    guess_err  = float(line[-10])
    underline  = float(line[-9])
    guess_true = float(line[-8])
    known_true = float(line[-7])
    only_opt   = float(line[-6])
    under_lcYes= float(line[-5])
    under_lcNo = float(line[-4])
    err_lc_err = float(line[-3])
    cause      = cause_list.find(line[-1])
    err_type = err_type_list.find(err_types[word])

    ratio, fixed_count, word_count = features1[word]

    inp = (np.log(max(ratio,1e-6)), np.log(max(fixed_count,1)), np.log(max(word_count,1)), uncertain, known_err, guess_err, underline, guess_true, known_true, only_opt, under_lcYes, under_lcNo, err_lc_err, cause, err_type)
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
