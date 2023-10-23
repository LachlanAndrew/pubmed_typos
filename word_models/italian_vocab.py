#!/usr/bin/python3

import sys
import pdb

global vocab
vocab = []

global suffixes
suffixes = {
  "0": ("mi", "ne", "sela", "si", "vene", "vi"),
  "1": ("mi", "ne", "sele", "si"),
  "2": ("la", "le", "lesi", "li", "lo"),
  "3": ("a", "e", "i", "o"),
  "4": ("i", "ici", "isi"),
  "5": ("e", "esi", "i", "isi"),
  "6": ("e", "ero", "i", "imo"),
  "7": ("mo", "no", "si", "te"),
  "8": ("ene", "i", "isi"),
  "9": ("mi", "mmo", "ndo"),
  ":": ("mmo", "mo", "ste", "sti", "te"),
  "=": ("mi", "ne", "si", "ti"),
  "+": ("evene", "evi", "igli", "ili", "imi", "iseli"),
}

# groups # $ and % seem not to be used
larger_groups_find = {
  "@": ("cene", "ci", "gli", "gliel3", "gliene"),
  "#": ("el3", "ene", "i"),
  "$": ("", "el3", "ene"),
  "%": ("el3", "ene", "4"),
}

larger_groups_expand = {
  "@": ("cene", "ci", "gli", "gliela", "gliele", "glieli", "glielo", "gliene"),
  "#": ("ela", "ele", "eli", "elo", "ene", "i"),
  "$": ("", "ela", "ele", "eli", "elo", "ene"),
  "%": ("ela", "ele", "eli", "elo", "ene", "i", "ici", "isi"),
}

prefixes = {
"0": ("all'", "bell'", "brav'", "c'", "coll'", "d'", "dall'", "dell'", "l'", "m'", "n'", "nell'", "quell'", "quest'", "s'", "sull'", "t'", "v'"),
"1": ('', "l'", "m'", "n'", "nell'", "quell'", "quest'", "s'", "sull'", "t'", "v'"),
"2": ("all'", "bell'", "brav'", "buon'", "ciascun'", "coll'", "d'", "dall'", "dell'", "l'", "nell'", "quell'", "quest'", "sull'", "un'"),
"3": ('', "bell'", "brav'", "c'", "coll'", "d'", "dall'", "dell'", "l'", "m'", "n'", "nell'", "quell'", "quest'", "s'", "sull'", "t'", "v'"),
"4": ('', "all'", "bell'", "brav'", "c'", "coll'", "d'", "dall'", "dell'", "l'", "m'", "n'", "nell'", "quell'", "quest'", "s'", "sull'", "t'", "v'"),
"5": ("all'", "c'", "coll'", "d'", "dall'", "dell'", "l'", "m'", "n'", "nell'", "quell'", "quest'", "s'", "sull'", "t'", "v'"),
"6": ("all'", "bell'", "brav'", "coll'", "d'", "dall'", "dell'", "l'", "nell'", "quell'", "quest'", "sull'"),
"7": ('', "bell'", "brav'", "buon'", "ciascun'", "coll'", "d'", "dall'", "dell'", "l'", "nell'", "quell'", "quest'", "sull'", "un'"),
"8": ('', "l'", "nell'", "quell'", "quest'", "sull'", "un'"),
"9": ('', "all'", "bell'", "brav'", "buon'", "ciascun'", "coll'", "d'", "dall'", "dell'", "l'", "nell'", "quell'", "quest'", "sull'", "un'"),
":": ('', "l'", "nell'", "quell'", "quest'", "sull'"),
"=": ('', "quell'", "quest'", "s'", "sull'", "t'", "v'"),
"+": ("buon'", "ciascun'", "un'"),
"*": ('', "all'", "c'", "coll'", "d'", "dall'", "dell'", "l'", "m'", "n'", "nell'", "quell'", "quest'", "s'", "sull'", "t'", "v'"),
"@": ("all'", "coll'", "d'", "dall'", "dell'", "l'", "nell'", "quell'", "quest'", "sull'"),
"#": ('', "c'", "coll'", "d'", "dall'", "dell'", "l'", "m'", "n'", "nell'", "quell'", "quest'", "s'", "sull'", "t'", "v'"),
"$": ('', "bell'", "brav'", "coll'", "d'", "dall'", "dell'", "l'", "nell'", "quell'", "quest'", "sull'"),
"%": ("c'", "m'", "n'", "s'", "t'", "v'"),
"^": ("all'", "ciascun'", "coll'", "d'", "dall'", "dell'", "l'", "nell'", "quell'", "quest'", "sull'", "un'"),
"&": ('', "all'", "bell'", "brav'", "coll'", "d'", "dall'", "dell'", "l'", "nell'", "quell'", "quest'", "sull'"),
"_": ("all'", "bell'", "brav'", "buon'", "c'", "ciascun'", "coll'", "d'", "dall'", "dell'", "l'", "m'", "n'", "nell'", "quell'", "quest'", "s'", "sull'", "t'", "un'", "v'"),
"+": ("all'", "bell'", "ciascun'", "coll'", "d'", "dall'", "dell'", "l'", "nell'", "quell'", "quest'", "sull'", "un'"),
";": ("all'", "bell'", "c'", "coll'", "d'", "dall'", "dell'", "l'", "m'", "n'", "nell'", "quell'", "quest'", "s'", "sull'", "t'", "v'"),
"?": ('', "quell'", "quest'", "sull'", "un'"),
"~": ("coll'", "dall'", "dell'", "quell'", "quest'"),
}


def known (word) :
  global vocab, suffixes
  if word in vocab :
    return True

  for s in suffixes :
    for suff in suffixes[s] :
      #if word.endswith(suff) : print ("A", word[0:-len(suff)]+s)
      if word.endswith(suff) and word[0:-len(suff)]+s in vocab :
        return True

  pref = word.find("'")
  if pref == -1 :
    return False

  prefix = word[0:pref+1]
  for p in prefixes :
    if prefix in prefixes[p] :
      if p+word[pref+1:] in vocab :
        return True
      for s in suffixes :
        for suff in suffixes[s] :
          #if word.endswith(suff) : print ("B", p+word[pref+1:-len(suff)]+s)
          if word.endswith(suff) and p+word[pref+1:-len(suff)]+s in vocab :
            return True

  return False

def read_vocab (filename, source_filename) :
  global vocab
  try :
    with open (filename, "r") as f:
      vocab = {line.strip() for line in f.readlines()}
      global suffixes
      suffixes.update(larger_groups_expand)

  except IOError :
    with open (source_filename, "r") as f :
      recent_words = []
      all_suff = {s:suffixes[s] for s in suffixes}
      all_suff.update (larger_groups_find)

      count = 0
      for line in f :
        #if count > 100000: break
        word = line.strip ()
        recent_words.append(word)
        for s in suffixes :
          if word.endswith (suffixes[s][-1]) :
            stem = word[0:-len(suffixes[s][-1])]

            all_match = True
            for suff in suffixes[s] :
              if not stem + suff in recent_words :
                all_match = False
                break

            if all_match :
              for suff in suffixes[s] :
                recent_words.remove(stem + suff)

              #for w in recent_words :
              #  print (w)
              #print ("+", stem + s)

              recent_words.append (stem + s)
              vocab.extend (recent_words)
              recent_words = []

              break

    print ("finding prefix clusters", file=sys.stderr)
    prefx_counts = {}
    prefx = {}
    for word in vocab :
      if "'" in word :
        stem = word[word.find("'")+1:]
        if not stem in prefx:
          prefx[stem] = []
        prefx[stem].append(word[0:word.find("'")+1])
      else :
        prefx[word] = [""]

    """
    print ("finding common sets of prefixes")
    for word in prefx :
      prefx_set = tuple(s for s in sorted (prefx[word]))
      if not prefx_set in prefx_counts :
        prefx_counts[prefx_set] = 0
      prefx_counts[prefx_set] += 1

    for prefxix in sorted(prefx_counts, key= lambda x:-(len(x)-1)*prefx_counts[x]) :
      print (prefxix, (len(prefxix)-1) * prefx_counts[prefxix], prefx_counts[prefxix])
    quit ()
    """
    
    print ("clustering by prefix", file=sys.stderr)
    prefix_sets = {}
    for p in prefixes :
      prefix_sets[p] = set(prefixes[p])

    new_vocab = []
    for stem in prefx :
      wp = tuple(s for s in sorted (prefx[stem]))
      done = False
      for p in prefixes :
        if wp == prefixes[p] :
          #print (stem, ''.join([a[0] for a in prefixes[p]]))
          #for pref in prefixes[p] :
          #  vocab.remove(pref + stem)

          new_vocab.append (p+stem)
          done = True
          break

      if not done :
        pref_set = set(prefx[stem])
        for p in prefix_sets :
          if prefix_sets[p].issubset (pref_set) :
            new_vocab.append(p+stem)
            pref_set.difference_update (prefix_sets[p])
        for p in pref_set :
          new_vocab.append (p+stem)
      

    # Cache for next time
    with open (filename, "w") as f:
      for word in new_vocab :
        print (word, file=f)

    vocab = new_vocab

    suffixes.update(larger_groups_expand)

if __name__ == "__main__" :
  read_vocab ("words_it_cache.txt", "words_it.txt")
  print ("read vocab")

  for word in ("abattericissimamente",
               "all'abbacchiaglieli",
               "all'abbacchiamene",        # 0abbacchiamene
               "hippopotamus",
               "c'abbacchiacene") :
    print (word, known(word))
