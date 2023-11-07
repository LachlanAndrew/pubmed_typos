#!/home/llandrew/anaconda3/bin/python
#!/usr/bin/python3

import sys
import pickle
import math

import pdb

import italian_vocab
import chinese

n = 4   # number of letters as context

def build_model (word_file, n) :
  """
  Build n-gram model of the words in  words_lang.txt
  """
  # read in all n+1 grams
  n_plus_1_gram_counts = {}
  with open (word_file, "r") as f :
    for word in f :
      if not word or word[0] == "#" or " " in word :
        continue
      word = "^"*n + word.strip() + "$"
      for i in range (len(word) - n) :
        n_plus_1_gram = word[i:i+n+1]
        if n_plus_1_gram not in n_plus_1_gram_counts :
          n_plus_1_gram_counts[n_plus_1_gram] = 1
        else :
          n_plus_1_gram_counts[n_plus_1_gram] += 1
  #with open ("tmpppp", "w") as f :
  #  for key in sorted(n_plus_1_gram_counts) :
  #    print (str({key: n_plus_1_gram_counts[key]})[1:-1], file=f)

  # Find conditional probability of n+1st from previous n-gram
  counts = {}
  n_grams = {x:{} for x in range(0,n+1)}
  for N in range (n, -1, -1) :
    n_gram = None
    keys = sorted (n_plus_1_gram_counts)
    keys.append ("sentinel")
    for ng in keys :
      next_n = ng[:-1]
      if n_gram != next_n :
        if n_gram == None :
          n_gram = next_n
        else :
          s = sum([counts[x] for x in counts])
          k = len(counts)
          if not n_gram.startswith('^^') :     # at most one ^ at the start
            #n_grams[N][n_gram] = {c:math.log (counts[c]/s) for c in counts}

            # partial prefix match method C
            n_grams[N][n_gram] = {c:math.log (counts[c]/(s+k)) for c in counts}
            n_grams[N][n_gram]["ESC"] = math.log (k/(s+k))

            ## partial prefix match method D
            #n_grams[N][n_gram] = {c:math.log ((counts[c] - k/2)/(s)) for c in counts}
            #n_grams[N][n_gram]["ESC"] = math.log (k/(2*s))

            n_grams[N][n_gram]["sum"] = s

          n_gram = next_n
          counts = {}

      if ng != "sentinel" :
        counts[ng[-1]] = n_plus_1_gram_counts[ng]

    # Calculate counts for shorter prefixes
    if N > 0 :
      new_n = {}
      for key in n_plus_1_gram_counts :
        suff = key[1:]
        if suff in new_n :
          new_n[suff] += n_plus_1_gram_counts[key]
        else :
          new_n[suff] = n_plus_1_gram_counts[key]
      n_plus_1_gram_counts = new_n

  # compress to variable n?

  for N in range (n) :
    n_grams[N+1].update(n_grams[N])

  return n_grams[n]

esc_counts = {}
non_esc_counts = {}
def word_prob (word, model, count_escapes=False) :
  word = "^" + word + "$"
  pos = 1       # char after ^
  log_likelihood = 0
  #print ("   ", end="")
  while pos < len(word) :
    done = False
    for i in range (pos) :
      history = word[i:pos]
      if history in model :
        try :
          log_likelihood += model[history][word[pos]]
          done = True
          pos += 1

          if count_escapes :
            k = min (len(model[history])-2, 18)       # exclude ESC, sum
            s = min (model[history]["sum"], 48)
            if k not in non_esc_counts :
              non_esc_counts[k] = {s: 1}
            elif s not in non_esc_counts[k] :
              non_esc_counts[k][s] = 1
            else :
              non_esc_counts[k][s] += 1

          break
        except KeyError:
          low = word[pos].lower()
          if low in model[history] :
            # Should penalize this
            log_likelihood += model[history][low]
            done = True
            pos += 1

            # TODO: reduce duplication of the above
            if count_escapes :
              k = min (len(model[history])-2, 18)       # exclude ESC, sum
              s = min (model[history]["sum"], 48)
              if k not in non_esc_counts :
                non_esc_counts[k] = {s: 1}
              elif s not in non_esc_counts[k] :
                non_esc_counts[k][s] = 1
              else :
                non_esc_counts[k][s] += 1

            break
          else :
            #pdb.set_trace ()
            #log_likelihood += -20
            log_likelihood += model[history]["ESC"]

            if count_escapes :
              k = min (len(model[history]) - 2, 18)     # exclude ESC, sum
              s = min (model[history]["sum"], 48)
              if k not in esc_counts :
                esc_counts[k] = {s: 1}
              elif s not in esc_counts[k] :
                esc_counts[k][s] = 1
              else :
                esc_counts[k][s] += 1

        #print (int(log_likelihood), end = " ")
        #log_likelihood -= 3*i     # penalize shorter histories

    if not done :       # Transition so unlikely, it was never seen
                        # Should use "smoothing", but this will disappear
                        # when the variable-length prefixes are implemented
      log_likelihood += -20
      #print (int(log_likelihood), end = " ")
      pos += 1

  #print()

  return log_likelihood / (len (word) - 1)      # didn't guess "^"
    

def guess_lang (word, models, topn = None, count_escapes=False) :
  other_penalty = 1.5
  if topn == None :
    best_prob = -1000000000
    best_lang = ""
    for lang in models :
      #print (lang, word, end="\t")
      #if lang == "zh": pdb.set_trace()
      score = word_prob (word, models[lang], count_escapes)
      if lang == "oth" :        # Hack: try to classify a word as a specific
        score *= other_penalty  #       language, not "other"
      if score > best_prob :
        best_prob = score
        best_lang = lang

  else :
    scores = []
    for lang in models :
      score = -word_prob (word, models[lang], count_escapes)
      if lang == "oth" :        # Hack: try to classify a word as a specific
        score *= other_penalty  #       language, not "other"
      scores.append ((score, lang))
    scores.sort()
    best_lang = [ s[1] for s in scores[0:topn]]
    best_prob = [-s[0] for s in scores[0:topn]]

  return best_lang, best_prob

filename_from_cmd_line = []
def filename_from_lang (lang) :
  if filename_from_cmd_line :
    f = filename_from_cmd_line[0]
  else :
    f = "word_model_"
  return f + lang + ".pkl"

def lang_list(langs,punctuation) :
  return punctuation+str(langs).replace(" ","").replace("'","")

def init (langs, prefix = None) :
  if prefix and not filename_from_cmd_line :
    filename_from_cmd_line.append (prefix)
  models = {}
  for lang in langs :
    with open (filename_from_lang (lang), "rb") as f :
      models[lang] = pickle.load (f)
  return models

if __name__ == "__main__" :
  eliminate_from_dictionaries = False
  topn = 1
  if len(sys.argv) > 2 :
    while sys.argv[1].startswith('-') :
      if sys.argv[1] == "-m" :
        if len (sys.argv) > 3 :
          filename_from_cmd_line.append(sys.argv[2])
          del sys.argv[1]
          del sys.argv[1]
          continue
        else :
          print ("-m needs model prefix", file=sys.stderr)
          exit(1)

      if sys.argv[1] == "-n" :
        if len (sys.argv) > 3 :
          topn = int(sys.argv[2])
          del sys.argv[1]
          del sys.argv[1]
          continue
        else :
          print ("-n needs ", file=sys.stderr)
          exit(1)

      if sys.argv[1] == "-d" :
        eliminate_from_dictionaries = True
        del sys.argv[1]
        continue

      sys.argv = {}     # flag error
      break

  if len(sys.argv) < 2 :
    print (f"usage: {sys.argv[0]} cmd [-m model] [-n topn] [-d]",
           file=sys.stderr)
    exit(1)

  if sys.argv[1] == "build" :
    for i in range (1, int(len(sys.argv) / 2)) :
      model = build_model(sys.argv[2*i+1], n)
      with open (filename_from_lang (sys.argv[2*i]), "wb") as f :
        pickle.dump (model, f)
      #with open ("tmppp", "w")  as f :
      #  for key in model :
      #    print (str({key:model[key]})[1:-1], file=f)

      #with open (sys.argv[2*i+1], "r") as f :
      #  for word in f :
      #    word = word.rstrip()
      #    if word :
      #      pr = word_prob (word, model)
      #      print (word, pr, pr * (len(word) + 1))

  if sys.argv[1] == "guess" :
    models = {}
    dicts = {}
    for lang in sys.argv[3:] :
      with open (filename_from_lang (lang), "rb") as f :
        models[lang] = pickle.load (f)
      if eliminate_from_dictionaries :
        if lang != "it" :
          with open ("words_" + lang + ".txt") as f :
            print (lang, end="...", file=sys.stderr, flush=True)
            dicts[lang] = {w.rstrip() for w in f.readlines()}

    if "it" in sys.argv[3:] :
      italian_vocab.read_vocab("words_it_cache.txt", "words_it.txt")

    count_escapes = (sys.argv[2] == "../checked_words.txt")

    with open (sys.argv[2], "r") as f :
      for word in f :
        word = word.rstrip()
        guesses, scores = guess_lang (word.lower(), models, topn, count_escapes)
        guess = ','.join(guesses)
        score = scores[0]

        # Annotate guess by which dictionaries the word is in
        if eliminate_from_dictionaries :
          dict_entries = []
          for lang in dicts :
            if (word.lower() in dicts[lang]
                or (len(word) > 1
                    and word[0].upper()+word[1:].lower() in dicts[lang])) :
              dict_entries.append(lang)

          if "it" in sys.argv[3:] and (italian_vocab.known(word)
                                    or italian_vocab.known(word.lower())) :
            dict_entries.append("it")

          if "zh" in sys.argv[3:] and ((chinese.known(word)
                                     or chinese.known(word.lower())
                                       ) and not "zh" in dict_entries) :
            dict_entries.append("zh")

          if "oth" in dict_entries :
            # TODO: replace by correct form
            dict_entries = [e for e in dict_entries if e != "oth"]

          if guesses[0] in dict_entries :
            if len (dict_entries) == 1:
              guess = "=" + guess
            else :
              dict_entries.remove(guesses[0])
              guess = guess+lang_list(dict_entries, "|")
          else :
            if dict_entries :
              guess = guess+lang_list(dict_entries, "?")

        #print (word, guess, score)

    if count_escapes :
      with open ("esc_counts.txt", "w") as f, open("esc_frac.txt", "w") as f1 :
        for k in range (1, 18+1) :
          for s in range (1, 48+1) :
            try :
              print (esc_counts[k][s] / (esc_counts[k][s] + non_esc_counts[k][s]),
                     end=" ", file=f1)
              print ("%d/%d" % (esc_counts[k][s], (esc_counts[k][s] + non_esc_counts[k][s])),
                     end=" ", file=f)
            except KeyError :
              print (0 if k not in esc_counts or s not in esc_counts[k] else 1,
                     end= " ", file=f1)
              print (0 if k not in esc_counts or s not in esc_counts[k] else 1,
                     end= " ", file=f)
          print (file=f)
          print (file=f1)
