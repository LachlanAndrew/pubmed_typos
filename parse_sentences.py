#!/usr/bin/python

import re
from unidecode import *
import sys
import gzip

import pdb

abbreviations = {
  "a.c.",
  "d.c.",
  "e.g.",
  "e.p.",
  "e.s.r.",
  "e.u.",
  "i.e.",
  "i.v.",
  "i.p.",
  "i.u.",
  "i.ci.",
  "i.m.",
  "n.m.r.",
  "p.cent",
  "p.o.",
  "r.t."
  "s.c.",
  "s.e.",
  "e.p.p.",
  "e.p.p.s.",
  "m.e.p.p.",
  "m.e.p.p.s.",
  "U.S.",
  "Ph.D.",
  "Mr.",
  "Mrs.",
  "Dr.",
  "Prof.",
}

abbrev = {}
aa = [a for a in abbreviations]
for a in aa :
  b = a.split(".")
  if b and b[-1] == '' :
    del b[-1]
  for c in range(1,len(b)) :
    key = ".".join(b[0:c])
    if key not in abbrev :
      abbrev[key] = []
    abbrev[key].append(b[c])

import known_errs
typos = {w: ('*', known_errs.known_errs[w]) for w in known_errs.known_errs}
known_errs.known_errs = {} # save memory

"""
# load typos
typos = {}
try :
  with open ("typos.txt", "r") as f :
    for line in f :
      line = line.split()
      typos[line[0][1:]] = [line[0][0]]
      if len(line) > 2 and line[1] == ":" :
        typos[line[0][1:]].append (line[2].strip('"'))
      else :
        typos[line[0][1:]].extend (line[1:])
except FileNotFoundError :
  print ("No file typos.txt; occurrences of known typos will not be printed")
  pass
"""

# load frequencies of words from a previous run
word_count = {}
try:
  with open ("word_counts.txt", "r") as f :
    for line in f :
      line = line.split()
      word_count[line[0]] = sum([int(w) for w in line[1:]])
except FileNotFoundError :
  print ("No file word_ranks.txt; hyphenation errors will not be detected")
as_two_words = {w:0 for w in word_count if "-" not in w}

# load words identified as pairs of words with no separating space
joined_words = {}
try:
  with open ("words_joined.txt", "r") as f :
    for line in f :
      line = line.split()
      joined_words[line[0]] = {"-": 0, " ": 0, "_": line[1]}
except FileNotFoundError :
  print ("No file words_joined.txt; run-together words will not be counted")

# load explicitly hyphenated words from a previous run
hyph_count = {}
space_not_hyphen = {}
hyphenations = {}
try:
  with open ("words_hyphenated.txt", "r") as f :
    for line in f :
      line = line.split()
      hyph_count[line[0]] = sum([int(w) for w in line[1:]])
      space_not_hyphen[line[0].replace ("-", "")] = 0

      # record all seen hyphenations of a given word
      run_together = line[0].replace("-", "")
      if run_together not in hyphenations :
        hyphenations[run_together] = []
      hyphenations[run_together].append(line[0])

except FileNotFoundError :
  print ("No file words_hyphenated.txt; missing hyphens will not be counted")

not_hyphenated = {
  "orang": ("utan", "utans"),
  "soy": ("bean",),
  "a": ("lone",),
  "ultra": ("violet", "sonic", "sound"),
  "poke": ("weed",),
  "tread": ("mill",),
  "hong": ("kong",),
  "post": ("operative",),
  "extra": ("corporeal",),
  "radioimmuno": ("assay",),
  "radio": ("nuclide",),
  "path": ("way", "ways"),
  "pace": ("maker",),
  "multi": ("disciplinary",),
  "I": ("n",),
  "be": ("en",),        # be en route etc.
  "f": ("or",),         # f or s

  "cortico": ("steroids",),
  "immuno": ("sorbent",),
  "immuno": ("histochemical",),
  "Ikappa": ("Balpha",),
  "Ikappa": ("Balpha",),
  "beri": ("beri",),
  "carcino": ("embryonic",),    #?
  "cardio": ("vascular",),      #?
  "cholangio": ("pancreatography","pancreaticography"),
  "ante": ("natal",),
  "the": ("re", "ir"),       # the re face, the ir spectrum
  "The": ("re", "ir"),       # the re face, the ir spectrum
  "nitrobenzyl": ("thioinosine",),
  "nigro": ("striatal",),
  "musculo": ("skeletal",),
  "echo": ("cardiography",),
  "product": ("ion",),
  "inhibit": ("ion",),
  "supra": ("clavicular", "spinatus"),
  "gastro": ("intestinal",),
  "cerebro": ("spinal",),
  "oncorna": ("virus",),
  "quinque": ("fasciatus",),
  "veru": ("montanum",),
  "typhi": ("murium",),
  "Hin": ("dIII", "fI"),

  "malon": ("dialdehyde",),
  "monoethylglycine": ("xylidide",),
  "dimethylphenyl": ("piperazinium",),
  "polyacryl": ("amide",),
  "triacyl": ("glycerols",),
  "acetyl": ("acetonate", "chloramphenicols", "homotaurinate", "salycilic"),
  "antipentylene": ("tetrazol",),
  "antiphosphatidyl": ("inositol", "serine"),
  "antiphosphoryl": ("choline",),
  "antipicorna": ("virus",),
  "cyclohexane": ("triones",),
  "diastereo": ("isomers", "selectivity"),
  "trimethyl": ("silyl",),

}

def is_english (text: str) :
  """
    Return true if text is a list of English sentences.
    Currently detected by "is English if it contains the word 'the'".
  """
  return text.find(" the ") != -1

def is_number (text: str) :
  try :
    float(text)
    return True
  except ValueError :
    return False

def parse (text, en_only = True) :
  """
  Parse text into words.
  Keep "." characters within words, like decimals and acronyms.
  Flag starts of sentences, so that we can tell if a capital is
  part of the work or just to mark the start of a sentence.
  """
  if en_only and not is_english(text) :
    return []

  sentences = byte_escapes(text)                            # \x## to byte
  sentences = sentences.replace("--", "—").split(".")        # unicode em-dash
  word_sentences = [re.findall("[-\\w']+|[\\W]", s) for s in sentences]

  joined = []
  first_word = True
  for i, s in enumerate (word_sentences) :
    ## re-join hyphenated words here
    #if "-" in s :
    #  new_s = []
    #  for w in s :
    #    if len(new_s) > 1 and new_s[-1] == '-' and (re.match("\w+", new_s[-2])) and re.match ("\w+", w) :
    #      new_s[-2] = new_s[-2] + new_s[-1] + w
    #      del new_s[-1]
    #    else :
    #      new_s.append(w)
    #  s = new_s

    if not(s) :
      continue

    # TODO: merge words with brackets in the middle, like
    # N-[8-R-dibenzo(b,f)oxepin-10-yl]-N'-methyl-piperazine-maleates
    # (Check "close bracket then text" and "text then open bracket",
    # with no spaces between the brackets.)

    # TODO: Separate quotes from single-quoted phrases 

    # Append to sentence list, or join this sentence to the previous
    join = False
    if joined : # if not first sentence
      if len (joined[-1]) == 0:
        last = None
        join = True
      else :
        last = joined[-1][-1]
        if last in abbrev and (not abbrev[last]
                                or s[0] in abbrev[last]) :
          join = True

        if last[-1] in "0123456789-" and s and s[0] and s[0][0] in "0123456789" :
          join = True

        # "<initial>." does not end a sentence, e.g., E. coli
        if (len (last) == 1 and last.isupper() and s[0] and s[0][0].islower()) :
          join = True

      #if joined[-1][0] == "(" :
      #  print (joined[-1])
      #  print ("***", s)
      #  pdb.set_trace ()

    if join :
      new_sentence = joined[-1][0:-1]
      not_punct = re.match("\w+", s[0])       # . was in acronym, so join it
      new_sentence.append((last + "." if last else "") + (s[0] if not_punct else ""))
      new_sentence.extend(s[1 if not_punct else 0 :])
      joined[-1] = new_sentence
    else :
      if (joined and s and len(s[0]) == 1 and unidecode(s[0]) in ")]}"
          and (len(s) == 1 or s[1] < "a" or s[1] > "z")) :
              # Closing bracket belongs with previous sentence
        joined[-1].append (s[0])
        del s[0]

      while (s and s[0] == " ") :
        del s[0]

      #if "The" in s and s[0] != "The" :
      #  print (s)
      #  pdb.set_trace ()

      if len(s) > 3 and s[0] == "(" and s[2] == ")" :
        joined.append(s[0:3])
        joined.append(s[3:])
      elif len(s) > 2 and unidecode(s[1]) == ")" :
        joined.append(s[0:2])
        joined.append(s[2:])
      else :
        joined.append(s)
        #if s[0] and s[0][0] >= "a" and s[0][0] <= "z" :
        #  print (line)
        #  print ("".join (joined[-2]))
        #  print (i, s)
        #  pdb.set_trace ()

    #if joined[-1][0] == "(" :
    #  print (joined[-1])
    #  print (s)
    #  pdb.set_trace ()

  return [[w for w in s if w != " "] for s in joined]

def byte_escapes (text) :
  """
  Expand any escaped 8-bit values encoded by \\x<d><d>.
  """
  s = bytes(text, encoding="utf-8").split(b'\\')
  if len (s) == 1 :
    return text

  # handle \\ in the original text, to escape a literal backslash
  literals = [i for i, ss in enumerate(s) if len(ss) == 0]
  try:
    if literals :
      if len(literals) >= 3 :
        # The pattern \\\\ yields three matches, not two.  Delete the mid one
        new_literals = [literals[0]]
        for n in literals[1:] :
          if n > new_literals[-1] + 1 :
            new_literals.append(n)
        literals = new_literals
      for i in reversed(literals) :
        if i > 0 :
          if i+1 < len(s) :
            s[i-1] = b"\\".join([s[i-1], s[i+1]])
            del s[i+1]
          else :
            s[i-1] = s[i-1]+b"\\"
          del s[i]
        else :
          s[i] = b"\\" + s[i+1]
          del s[i+1]
  except IndexError:
    print ("Could not parse", text, literals, s)
    retval = bytes([b for b in text if b < 128]).decode ()
    print ("Invalid unicode.  Returning ASCII portion:", retval)
    return retval

  # First part of each string in s[1:] is a byte escape.
  # Decode them.
  parts = [s[0]]
  for p in s[1:] :
    if len(p) >= 3 and p.startswith (b'x') :     # 8-bit escapes
      try :
        parts.append(bytes([int(p[1:3], base=16)]))
      except ValueError :
        print ("Invalid Unicode escape in", p)
        parts.append(p[1:3])
      parts.append(p[3:])
    elif len(p) >= 2 and p[0] in b"'":           # other escapes
      parts.append(p)
    else :
      parts.append(b'\\')                        # unrecognised; perhaps literal
      parts.append(p)

  if any([p.find(b"xbc") != -1 for p in parts]) :
    print (parts)
    pdb.set_trace ()
  try :
    return b"".join (parts).decode()
  except UnicodeDecodeError :
    retval = bytes([b for b in b"".join(parts) if b < 128]).decode ()
    print ("Invalid unicode.  Returning ASCII portion:", retval)
    return retval
    

lexicon = {}
count_by_journal = {}
hyphen_prefix = {}      # possible hyphenated words, part before hyphen
hyphen_suffix = {}      # possible hyphenated words, part after  hyphen
after_number = {}
before_number = {}

def count (dictionary, key) :
  if key in dictionary :
    dictionary[key] += 1
  else :
    dictionary[key] = 1

def count_count (dictionary, key1, key2, init = None) :
  if not key1 in dictionary :
    dictionary[key1] = init if init != None else {}

  if not key2 in dictionary[key1] :
    dictionary[key1][key2] = 0

  dictionary[key1][key2] += 1

filename = sys.argv[1] if len(sys.argv) > 1 else "abstracts.txt.gz"

max_lines = -1  # unlimited

#try :
for loop in range(1) :
  with (gzip.open (filename, "r") if filename.endswith(".gz") else open (filename, "rb")) as f :
    for line in f :
      max_lines -= 1
      if max_lines == 0 :
        break

      parts = line.strip().decode("utf-8").split('"')
      if len (parts) < 3 :
        print ("Error", parts, file=sys.stderr)
        continue
      ID = parts[0] + '"' + parts[1].replace("”", '"') + '"'
      line = '"'.join(parts[2:])

      # Remove PubMed ID and volume(number):pages,year
      try :
        journal = " ".join(parts[0].split()[1:-1])
      except IndexError :
        if parts :
          journal = parts[0]
          print ("odd journal name:", journal)
        else :
          print ("Can't find journal in parts:", parts)
          continue
        pass

      try :
        if "(" in journal :       # volume(number):pages,year had a space in it
          journal = journal[:journal.find("(")]

        # Remove trailing distractions from journal name
        journal = journal + " "   # force loop below to execute at least once
        ii = len(journal)
        while ii and journal[ii-1] in "0123456789.(: -" :
          ii -= 1
          for suff in (" Suppl", " Supplement", " Spec", " Pt") :
            if journal[:ii].endswith(suff) :
              ii -= len (suff)
        journal = journal[:ii]
      except IndexError as e :
        print ("Error:", e)
        print ("journal", journal)
        #pdb.set_trace ()

      if journal not in count_by_journal :
        # counts of: articles, articles with errors, sentences with errors
        count_by_journal[journal] = {"a": 0, "e": 0, "s": 0}
      count_by_journal[journal]["a"] += 1

      sentences = parse (line)

      # check for occurrence of previously-found typos
      if typos :
        if any ([any ([w in typos for w in s]) for s in sentences]) :
          for s in sentences :
            w = [w for w in s if w in typos]
            if w :
              for ww in w :
                print ("TYPO", ''.join(['"',ww,'": "',
                                       (typos[ww][1] if len(typos[ww])>1 else ""),
                                       '"']),
                       ID, (" ".join(s)).replace(ww, "*"+ww.upper()+"*"),
                       file=sys.stderr)
                count_by_journal[journal]["s"] += 1

          count_by_journal[journal]["e"] += 1

          continue

      # check for broken words (hyphenation, then hyphen deleted)
      if word_count :
        for s in sentences :
          joined = [s[i]+s[i+1] for i in range(len(s)-1)]
          for i in range(len(s)-1) :
            #if s[i] == "ure" : pdb.set_trace ()
            if joined[i] in word_count and s[i] and s[i+1] :
              if "-" not in joined[i] :
                as_two_words[joined[i]] += 1

              try :
                parts = min ( 2 * max([word_count[s[i]], word_count[s[i+1]]]),
                             300 * min([word_count[s[i]], word_count[s[i+1]]]))
              except KeyError :
                parts = 0

              if ( parts < word_count[joined[i]]
                   and (s[i].lower() not in not_hyphenated
                        or s[i+1].lower() not in not_hyphenated[s[i].lower()]) ) :
                count_count(hyphen_prefix, s[i], joined[i])
                count_count(hyphen_suffix, s[i+1], joined[i])
                pair = s[i] + " " + s[i+1]
                print ("HYPHEN", ''.join(['"',pair,'": "',joined[i],'"']),
                       ID, (" ".join(s)).replace(pair, "*"+pair.upper()+"*"),
                       file=sys.stderr)

              if joined[i] in joined_words :
                count_count(joined_words, joined[i], " ")

      # Check relative frequencies of
      # (a) hyphenated word,
      # (b) space-separated word,
      # (c) run-together word
      if hyphenations :
        for s in sentences :
          pairs = ["-".join((s[i], s[i+1])) for i in range(len(s)-1)]
          for h in pairs :
            if h in hyph_count :
              space_not_hyphen[h.replace("-","")] += 1

      # Check for words before and after numbers
      for s in sentences :
        for i, w in enumerate (s) :
          if is_number (w) :
            if i < len(s)-1 and not is_number(s[i+1]) :
              count (after_number, s[i+1])
              if i+2 < len(s)-1 and s[i+2] == "/" :
                count (after_number, s[i+3])
            if i > 0 :
              pre = i-1 if  s[i-1] != "=" else i-2
              if pre >= 0 and not is_number(s[pre]) :
                count (before_number, s[pre])
              
      
      # count words
      for s in sentences :
        first_word = True
        for i, w in enumerate(s) :
          if len(w) > 1 or re.match(r"[-\w']+", w) :
            if w not in lexicon :
              lexicon[w] = {"f": 0, "o": 0}
              #print(w, file=sys.stderr)

            #if w == "The" and not first_word :
            #  print (s)
            #  pdb.set_trace ()

            lexicon[w]["f" if first_word else "o"] += 1
            first_word = False
#except Exception as e :
#  try :
#    print (e)
#  except :
#    pass

# Count hyphenated occurrences of words that seem to be formed of two words
if joined_words :
  for w in lexicon :
    if '-' in w :
      ww = w.split("-")
      if len(ww) == 2 :
        wj = "".join(ww)
        if wj in joined_words :
          count_count(joined_words, wj, "-")

# Total number of occurrences of word
for w in lexicon :
  lexicon[w]["s"] = lexicon[w]["f"] + lexicon[w]["o"]

print ("--- run together")
for w in joined_words :
  if w in lexicon :
    j = joined_words[w]
    cases = lexicon[w]["s"]
    print (j["_"], cases/max(j["-"] + j[" "], 1e-6), cases, j["-"], j[" "])

print ("--- errors by journal")
for j in sorted (count_by_journal, key = lambda w: -count_by_journal[w]["e"]/count_by_journal[w]["a"]) :
  c = count_by_journal[j]
  if c["e"] :
    print ("%4d %4d %4d" % (c["s"], c["e"], c["a"]), j)

print ("--- fragments")
prefix_count = {w:sum([hyphen_prefix[w][i] for i in hyphen_prefix[w]]) for w in hyphen_prefix}
for j in sorted (hyphen_prefix, key = lambda w : -prefix_count[w]) :
  print (j+'-', hyphen_prefix[j])

suffix_count = {w:sum([hyphen_suffix[w][i] for i in hyphen_suffix[w]]) for w in hyphen_suffix}
for j in sorted (hyphen_suffix, key = lambda w : -suffix_count[w]) :
  print ('-'+j, hyphen_suffix[j])

print ("--- hyphenations: together, hyphenated, separate (ratios)")
for w in lexicon :
  if w in hyphenations : # skip words that will be covered by - version
    continue
  if w in hyph_count : # Check for space and run-together versions
    word = w.replace("-", "")
    hyph = hyph_count[w]
  else :        # if spaced version exists but no hyphenated version, print that
    word = w
    hyph = 0
  together = lexicon[word]['s'] if word in lexicon else 0
  separate = space_not_hyphen[word] if word in space_not_hyphen else 0
  if together > 0 and hyph > 100 * together :
    print (str({word:w})[1:-1] + ",  #", together, hyph, separate, hyph/total, separate/total)
  elif sum([1 if hyph != 0 else 0,
          1 if separate != 0 else 0,
          1 if together else 0]) > 1 :
    total = together + hyph + separate
    print (w, together, hyph, separate, hyph/total, separate/total)

print("---")
# Print words that come before or after a number over 50% of the time
# like units, or fmax=...
unit_like = {}
for w in lexicon :
  before = before_number[w] if w in before_number else 0
  after  = after_number [w] if w in after_number  else 0
  if before + after > lexicon[w]['s'] / 2 :
    unit_like[w] = ((before+after)/lexicon[w]['s'], before, after)
for w in sorted (unit_like, key = lambda x : -unit_like[x][0]) :
  before = before_number[w] if w in before_number else 0
  after  = after_number [w] if w in after_number  else 0
  print (w, unit_like[w][1]/lexicon[w]['s'], unit_like[w][2]/lexicon[w]['s'])

print ("---")
for w in sorted(lexicon, key = lambda w: (-lexicon[w]["f"]-lexicon[w]["o"], w)) :
  print (w, lexicon[w]["o"], lexicon[w]["f"],
         prefix_count[w] if w in prefix_count else 0,
         suffix_count[w] if w in suffix_count else 0,
        )
