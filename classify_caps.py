#!/usr/bin/python

import re
from unidecode import *
import sys
import gzip

import pdb

import known_errs
typos = {w: ('*', known_errs.known_errs[w]) for w in known_errs.known_errs}
known_errs.known_errs = {} # save memory

"""
# load frequencies of words from a previous run
word_count = {}
try:
  has_cap = re.compile ("^[a-zA-Z]*[A-Z][a-zA-Z]* ")
  with open ("words_ranked_caps_1-1166.txt", "r") as f :
    for line in f :
      line = line.split()
      if has_cap.match (line) :
        word_count[line[0]] = sum([int(w) for w in line[1:]])
except FileNotFoundError :
  print ("No file word_counts.txt; hyphenation errors will not be detected")
"""

past_class = {}
try :
  with open ("words_classified_caps_1-1166.txt", "r") as f :
    for line in f :
      line = line.strip().split()
      if len (line) == 0 or len (line[1]) == 0 :
        continue
      word = line[0][1:] if line[0][1].isalnum () else (line[0][2:] if len(line) > 2 else "")
      past_class [word] = [line[0][0], line[1]]
      past_class [word].extend(line[2:])
except FileNotFoundError :
  print ("No previous classification of words.  Run likely_errors.py")

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

    if not(s) :
      continue

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
#max_lines = 80000

#try :
abbrev = re.compile (r"(?:\b\w*[A-Z]\w* ){1,10}\(\w*\)")
odd_caps = re.compile (r"\b(?:[a-z]+[A-Z]|\w+[A-Z][a-z]|\w*[a-z][A-Z])\w*")
species = re.compile(r"\b\w[a-z]+[A-Z]\. *[a-z]{3,}\b")
in_brackets = re.compile(r"\(\w*[A-Z]\w*\)")
any_cap = re.compile (r"\b\w*[A-Z]\w*\b")

surname = re.compile(r"\b[A-Z][a-z]*(?: et al|, [A-Z]\.)")
abbrev1 = re.compile(r"\b\w*[A-Z]\w* (?:\w* ){1,6}\([A-Z]{2,}\)")
abbrev2 = re.compile(r"\b[A-Z]{4,} (?:\w* ){,2}\(\w[-\w ]*\)")
abbrev3 = re.compile(r"\b[A-Z][-A-Z]+ \([A-Za-z][-A-Za-z ]*\)")
# r.e. for ACRONYM (ExPanSiON)
# r.e. for Surname et al
# r.e. for Surname, F.

normal_caps = {}
all_caps    = {}
is_odd_many = {}
is_odd_few  = {}
brackets    = {}
is_abbrev   = {}
surnames    = {}
species_join = {}
odd_for_abbrev = {}

en_only = True
for loop in range(1) :
  with (gzip.open (filename, "r") if filename.endswith(".gz") else open (filename, "rb")) as f :
    for line in f :
      max_lines -= 1
      if max_lines == 0 :
        break

      ll = line.strip().decode("utf-8")
      parts = ll.split('"')
      if len (parts) < 3 :
        done = False
        for patt in (":\d+(?:-\d+)?,[12][890]\d\d ", ",[12][890]\d\d ",
                     ":\d+(?:-\d+)? ", ":\w+(?:-\w+)?(?:[12][890]\d\d)? ") :
          pp = re.split(patt, ll, maxsplit=1)
          if len (pp) == 2 :
            parts = [ll[:len(ll)-len(pp[1])].strip(), "", ll[len(ll)-len(pp[1]):].strip()]
            #print (parts, file=sys.stderr)
            done = True
            break
        if not done :
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

      if en_only and not is_english(line) :
        continue

      ll = byte_escapes(line)                            # \x## to byte

      # Check if it contains lowercaseL. species
      # Check if it contains SiLly ACronym Keys (SLACK)
      # Check if it contains (WordWithCaps) in brackets
      # Check if it contains other words with oDdCApitaLIzatioN

      mc = any_cap.findall (ll)
      if mc :
        mo = odd_caps.findall (ll)
        ms = species.findall (ll)
        ma = (abbrev.findall (ll) if "(" in ll and not re.findall("[A-Z ]{60,}", ll)
              else [])
        ma1= abbrev1.findall (ll)
        ma2= abbrev2.findall (ll)
        ma3= abbrev3.findall (ll)
        mb = in_brackets.findall (ll)
        mn = surname.findall (ll)

        for a in ms :
          w = a.split(".")[0]
          count(species_join, w)
          mo = [ww for ww in mo if ww != w]
          mc = [ww for ww in mc if ww != w]


        # abbrev1 catches too many phrases, so cull those that don't match
        ma1_tidied = []
        for i, p in enumerate(ma1) :
          done = False
          pp = p.split()
          acronym = pp[-1][1:-1]
          if len (acronym) < len (pp) :
            lead_up = pp[-len(acronym)-1:-1]
            initials = "".join([a[0] for a in lead_up]).lower()
            if initials == acronym.lower() :
              pp = "".join ([" ".join(lead_up), " (", acronym, ")"])
              #print ("ab*", [pp, p])
              p = pp
              done = True
            elif initials[-1] == acronym[-1].lower() :
              lead_up2 = [w for w in pp if len(w) > 2]
              if len (acronym) < len (lead_up2) :
                lead_up2 = lead_up2[-len(acronym)-1:-1]
                initials2 = "".join([a[0] for a in lead_up2]).lower()
                if initials2 == acronym.lower() :
                  pp = "".join ([" ".join(lead_up2), " (", acronym, ")"])
                  #print ("ab!", [pp, p])
                  p = pp
                  done = True

          if not done :
            capitals = [(j,c) for j, c in enumerate(p)
                          if c.isupper() and j < len(p) - len (pp[-1])]
            if len (capitals) >= len (acronym) :
              start_from = capitals[-len (acronym)][0]
              start_from = p[start_from].rfind(" ") + 1
              actual_capitals = "".join([c[1] for c in capitals[-len(acronym):]])
              if actual_capitals == acronym.upper() :
                #print ("ab+", [p[start_from:], p])
                p = p[start_from:]
                done = True

          if not done :
            r = re.search(r".*\b(" + ".*".join(acronym) + "[^ ]*)",
                         " ".join(pp[:-1]), flags=re.I)
            if r :
              #print ("ab=", [r.group(1), p])
              p = "".join ([r.group(1), " (", acronym, ")"])
              done = True

          if done :
            ma1_tidied.append(p)

        #if ma1_tidied :
        #  print ("ab", ma1_tidied)

        for abr in (ma, ma1_tidied, ma2, ma3) :
          for a in abr :
            for i, w in enumerate(a.split()) :
              done = False
              if w.startswith("(") and w.endswith (")") :
                w = w[1:-1]
                count(is_abbrev, w)
                mb = [ww for ww in mb if ww != w]
                done = True
              elif abr in (ma2, ma3) :
                if i == 0 :
                  count(is_abbrev, w)
                  done = True
                else :
                  w = w.lstrip("(").rstrip(")")

              if not done :
                if odd_caps.findall(w) :
                  #print ("ab", w)
                  count(odd_for_abbrev, w)
                else :
                  # Normal capitalization before a bracket
                  continue

              mo = [ww for ww in mo if ww != w]
              mc = [ww for ww in mc if ww != w]

        for a in mb :
          w = a[1:-1]
          count(brackets, w)
          mo = [ww for ww in mo if ww != w]
          mc = [ww for ww in mc if ww != w]

        for a in mn :
          count(surnames, a)
          mo = [ww for ww in mo if ww != a]
          mc = [ww for ww in mc if ww != a]

        for a in mo :
          if a not in is_odd_many and a not in is_odd_few :
            pos = ll.find(a)
            print (a, ll[max(0, pos-100): min (pos+100, len(ll))])
          count(is_odd_many if len(mo) > 4 else is_odd_few, a)
          mc = [ww for ww in mc if ww != a]

        for a in mc :
          count(normal_caps if a[1:].islower() else all_caps, a)


#except Exception as e :
#  try :
#    print (e)
#  except :
#    pass

all_words = set(normal_caps.keys()).union(all_caps.keys()).union(is_odd_many.keys()).union(is_odd_few.keys()).union(brackets.keys()).union(is_abbrev.keys()).union(species_join.keys()).union(odd_for_abbrev.keys()).union(is_abbrev.keys())


for w in all_words :
  print (w, normal_caps [w] if w in normal_caps  else 0,
            all_caps    [w] if w in all_caps     else 0,
            "odd",
            is_odd_many [w] if w in is_odd_many  else 0,
            is_odd_few  [w] if w in is_odd_few   else 0,
            "br",
            brackets    [w] if w in brackets     else 0,
            is_abbrev   [w] if w in is_abbrev    else 0,
            "sp",
            species_join[w] if w in species_join else 0,
            surnames    [w] if w in surnames     else 0,
            "abr",
            is_abbrev  [w] if w in is_abbrev     else 0,
            odd_for_abbrev[w] if w in odd_for_abbrev else 0,
            past_class [w] if w in past_class    else [],
            )
