#!/home/llandrew/anaconda3/bin/python
#!/usr/bin/python3

import sys
import os
import pdb
import time
import wikipediaapi
from wiktionaryparser import WiktionaryParser

wiki_wiki = wikipediaapi.Wikipedia('en')
wiktionary = WiktionaryParser ()


languages = ["Persian", "Farsi", "Egyptian", "Tagalog", "Filipino",
             "French", "German", "Tamil", "Portuguese", "Italian",
             "Sanskrit", "Arabic", "Hindi", "Tigrinya", "Mongolian",
             "Burmese", "Macedonian", "Hawaiian", "Hebrew",
             "Malayalam", "Tibetan", "Greek", "Spanish", "Avestan",
             "Japanese", "Somali", "Chinese", "Irish", "Bengali", "Urdu",
             "Jamaican", "Croatian", "Hindustani", "Bulgarian",
             "Yiddish", "Turkish", "Korean", "Russian", "Gaelic",
             "Afrikaans", "Vietnamese", "Zulu", "Polish", "Swahili",
             "Belarusian", "Ukrainian", "Thai", "Swedish", "Norwegian",
             "Maori", "Māori", "Samoan", "Hawaiian", "Hawai'ian",
             "Cyrillic", "Estonian", "Danish",
             "legal"]
other_keywords = {"PLC": "Trademark", "trade name": "Trademark",
                  "Inc.": "Trademark", "developed by": "Trademark",
                  "brand name": "Trademark", "LLC": "Trademark",
                  "company": "Trademark", "corporation": "Trademark",
                  "trading as": "Trademark", "retailer": "Trademark",
                  "franchise": "Trademark", "trade mark": "Trademark",
                  "open-source": "Trademark", "album": "Trademark",
                  "trademark": "Trademark",
                  "is a given name": "Name", "is a surname": "Name",
                  "is a name": "Name", "is a male given name": "Name",
                  "is a female given name": "Name", "(born": "Name",
                  "drug": "Medical", "peptide": "Medical", "gene ": "Medical",
                  "protein": "Medical", "receptor": "Medical",
                  "ligand": "Medical", "flavone": "Medical",
                  "nucleoside": "Medical", "transcriptase": "Medical",
                  "nucleotide": "Medical", "aptamer": "Medical",
                  "zyme": "Medical", "dichloro": "Medical",
                  "intravenous": "Medical", "medicine": "Medical",
                  "otrophic": "Medical", "therapeutic": "Medical",
                  "diagnostic": "Medical", "psychological": "Medical",
                  "hormone": "Medical", "amino": "Medical",
                  "pharmacol": "Medical", "fumigant": "Medical",
                  "epinephrine": "Medical", "phenyl": "Medical",
                  "alkaloid": "Medical", "telomer": "Medical",
                  "oligomer": "Medical", "glycoside": "Medical",
                  "benzamide": "Medical", "clinical trial": "Medical",
                  "glycosyl": "Medical",
                  "superfamily": "Taxonomy", " clade": "Taxonomy",
                  "genus": "Taxonomy", "genera ": "Taxonomy",
                  "infraorder": "Taxonomy",
                  "species": "Taxonomy",
                  "mineral": "Geology", "metamorphic": "Geology",
                  "igneous": "Geology", "sedimentary": "Geology",
                  "subvolcanic": "Geology", "mantle-derived": "Geology",
                  "bedrock": "Geology", "lithosphere": "Geology",
                  "Italy": "Italian",
                  "France": "French",
                  "Germany": "German",
                  "Greece": "Greek",
                  "Indonesia": "Indonesian",
                  "Afghanistan": "Arabic",
                  "Azerbaijan": "Azerbaijani",
                  "Iraq": "Persian",
                  "Tibet": "Tibetan",
                  "India": "Hindi",
                  "Bollywood": "Hindi",
                  "Hindustani": "Hindi",
                  "South Asia": "Hindi",
                  "Malawi": "Chichewa",
                  "Croatia": "Croatian",
                  "Celtic": "Gaelic",
                  "Hangul": "Korean",
                  "Bulgaria": "Bulgarian",
                  "Nepal": "Nepalese"}

def has_Japanese (text) :
  return any ([ord(c) >= 12353 and ord(c) <= 12436 for c in text])

def has_Chinese (text) :
  return any ([ord(c) >= 0x4e00 for c in text]) and not has_Japanese (text)

def has_Korean (text) :
  return any ([ord(c) >= 0x1100 and ord(c) <= 0x11ff for c in text])

def has_English_suffix (word) :
  suffixes = {
    3: ("oid", "ist", "ism", "age", "box", "ers", "ors", "ing", "tor", "ent",
        "ies", "ium", "ial", "ise", "ize", "ied", "all"),
    4: ("oids", "tize", "tise", "ment", "ance", "ence", "hood", "iece", "ship",
        "gram", "head", "line", "book", "room", "ette", "less", "some", "iest",
        "life", "bank", "tors", "ised", "ized", "ises", "izes", "ists", "ions",
        "ings", "long", "town", "icle", "enty", "neck", "ials", "side", "ally",
        "ness", "tude"),
    5: ("ation", "ative", "graph", "ioned", "ional", "genic", "nymic", "iancy",
        "entlyl", "ively", "ingly", "antly", "ously", "edly", "ately", "ishly",
        "lessly", "fully", "somely", "larly", "istic", "boxes", "holic",
        "flora", "ments", "books", "lines", "heads", "rooms", "grams", "hoods",
        "ships", "icles", "ments", "ettes", "cracy", "aways"),
    6: ("graphy", "eaded", "mental", "ionist", "ionism", "holics", "nesses")
  }    

  for k in suffixes :
    if len (word) > k + 3 :
      if word[-k:] in suffixes[k] :
        return True

  return False
             

def guess_language (text, word, title, interactive = True, default = "", has_word = None) :
  # Don't override manual default.
  # Should check it, but too much plumbing for now
  if default.startswith("*") :
    return default

  for patt in ("\nAlternative spelling of ",
               "\nAlternative form of ",
               ") Alternative form of ") :
    pos = text.find(patt)
    if pos >= 0 :
      return ("&" + text[pos + len (patt):])

  for patt in ("\nArchaic spelling of ",
               "\nMisspelling of ") :
    pos = text.find(patt)
    if pos >= 0 :
      return ("!" + text[pos + len (patt):])

  low = " " + text.lower ()
  low_title = title.lower()
  if word.replace(" ", "") == low_title.replace(" ", "") and word != low_title :
    return "_"+low_title.replace(" ", "_")
  if word.replace("-", "") == low_title.replace("-", "") and word != low_title :
    if " " in low_title :
      low_title = low_title[0:low_title.find(" ")-1]
    return "-"+low_title

  candidates = {}
  full_candidates = {}
  for language in languages :
    pos = low.find(language.lower())
    if pos >= 0 :
      candidates[language] = pos
      full_candidates[language] = pos

  if len (candidates) == 1 and list(candidates.values())[0] < 1000 :
    #print ("A")
    return list(candidates)[0]
  elif set(candidates) == {"Tagalog", "Filipino"} :
    #print ("B")
    return "Tagalog"

  
  if True or len (candidates) == 0 :
    # Look for keywords.  TODO: Should check they are the complete word.
    for keyword in other_keywords :
      pos = low.find(keyword.lower())
      if pos >= 0 :
        candidates[other_keywords[keyword]] = pos
        full_candidates["".join([other_keywords[keyword]," (",keyword,")"])] = pos
  if len (candidates) == 1 :
    #print ("C")
    by_pos = {full_candidates[k]:k for k in full_candidates}
    positions = list(by_pos)
    positions.sort()
    if not positions :
      pdb.set_trace ()
    return "/".join([by_pos[a] for a in positions])
  else :
    print (word, candidates)

  if (title and title == title.upper()) or text.find(word.upper()) >= 0 :
    #print ("D")
    return "acronym"

  if not text.find ("may refer to") >= 0 :
    if "Medical" in candidates :
      #print ("E")
      return "/".join([a for a in full_candidates if a.startswith("Medical")])
    elif "Taxonomy" in candidates :
      #print ("F")
      return "/".join([a for a in full_candidates if a.startswith("Taxonomy")])

  best_so_far = ""
  if len (candidates) >= 2 :
    by_pos = {candidates[k]:k for k in candidates}
    positions = list(by_pos)
    positions.sort()
    lang = by_pos[positions[0]]
    # len(position) == 1 if collision of position values
    if len (positions) == 1 or 2 * positions[0] < positions[1] :
      #print ("G")
      return "/".join([a for a in full_candidates if a.startswith(lang)])
    else :
      best_so_far = lang

  prefix = low[1:low.find(":")+1]
  if len (prefix) < 200 and prefix.find (" (") >= 0 :
    guess = prefix[prefix.rfind("(")+1:]
    if ")" in guess :
      guess = guess[0:guess.find(")") - 1]
    guess = ''.join ([a for a in guess if (a >= 'a' and a <= 'z') or a in " -/"]).strip()
    if guess.endswith (" pronunciation") :
      guess = guess[0:guess.rfind(" pronunciation")]
    if guess.startswith ("from the ") :
      guess = guess[guess.find("from the ")+9 :]
    if guess.startswith ("from ") :
      guess = guess[guess.find("from ")+5 :]
    guess = guess.strip().title()
    if len (guess) > 30 :
      guess = ""
  else :
    guess = ""

  if guess and (guess in candidates or guess == best_so_far) :
    #print ("H")
    return guess

  if best_so_far and best_so_far == default :
    #print ("I")
    return best_so_far

  if not guess and best_so_far :
    guess = best_so_far

  if not guess :
    lines = text.split("\n")
    if all (any ([line.find(p) >= 0
                  for p in ("(slang",      "slang)",
                            "(informal",   "informal)",
                            "(colloquial", "colloquial)",
                            "(childish",   "childish)",
                            "(nonstandard","nonstandard)",
                            "(dialect",    "dialect)")
                 ]) for line in lines[1:]) :
      return "^"

  if not guess and default :
    guess = default.replace("*", "")    # * = manually selected

  if interactive :
    print ("="*40)
    if has_word : 
      pos = low.find(word) - 1
      if pos >= 400 :
        text = text[0:200] + "\n-------\n" + text[pos-200:pos] + "***" + text[pos:pos+1000]
      elif pos >= 0 :
        text = text[0:pos] + "***" + text[pos:pos+1000]
      else :
        has_word = False
    print (text)
    if not full_candidates :
      full_candidates = candidates
    if full_candidates :
      print (full_candidates)
    if has_word == None :
      has_word = low.find(word)>=0
    has_word = " (missing)" if not has_word else ""
    print (f"{title}-> Please guess the language of **{word}**{has_word}",
           "("+guess+")" if guess else "")

    done = False
    while not done :
      done = True
      language = sys.stdin.readline ()
      language = guess if language == "\n" else language.rstrip()

      if (language and not language in other_keywords.values()
            and language[0].isupper () and not language.startswith("English")) :
        languages.append (language)
      if language == "save" :
        save (entries, "wikipedia_output.py")
        done = False
        print ("Saved.  Please guess the language.")
      if language == "quit" :
        exit ()
      language = "*" + language # * = manually selected

    print (language)
    return language

  # Return candidates in the order in which evidence occurs
  if full_candidates :
    by_pos = {full_candidates[k]:k for k in full_candidates}
    positions = list(by_pos)
    positions.sort()
    if not positions :
      pdb.set_trace ()
    return "?" + "/".join([by_pos[a] for a in positions])

  if default and default != "English" :
    print ("Default", default, "but returning nothing")
    #pdb.set_trace ()

  # Out of ideas
  return ""

def save (dictionary, filename, all_read = True) :
  try :
    os.rename(filename, filename+".bak")
  except Exception as e:
    # todo: discarde no such file excepton
    print (e)
    import pdb; pdb.set_trace()

  with open (filename, "w") as f :
    print (filename.replace (".py", ""), "= {", file=f)
    for key in dictionary :
      string = str({key:dictionary[key]})[1:-1]
      print (string+",", file=f, flush=True)
    print ("}", file=f)
    print ("all_read =", all_read, file=f)


#####################
if len (sys.argv) > 1 and sys.argv[1] == "no_entry" :
  from wikipedia_output import wikipedia_output
  # failed attempt
  group = {"dh": "Hindi",
           "bh": "Hindi",
           "^ng": "Chinese",
           "eong$": "Korean",
           "^mb": "African",
           "kh": "Arabic",
           "szcz": "Polish",
           "rz": "Polish",
          }
  with open ("wikipedia_input.txt", "r") as f : #, open ("wikipedia_output", "a") as g :
    for word in f :
      word = word.rstrip ()
      if not word in wikipedia_output :
        if has_English_suffix(word) :
          print (f'"{word}": "English",')
          continue

        word_plus = "^" + word + "$"
        found = False
        for seq in group :
          if word_plus.find(seq) >= 0 :
            print (f'"{word}": "{group[seq]}",')
            found = True
            break
        if found :
          continue

        print (f'"{word}": "unclassified",')

  quit()
  

#####################
try :
  from wikipedia_output import wikipedia_output, all_read
  entries = wikipedia_output
  load_wiki = False
except :
  entries = {}
  load_wiki = True

if load_wiki or not all_read :
  count = 0
  with open ("wikipedia_input.txt", "r") as f : #, open ("wikipedia_output", "a") as g :
    for word in f :
      word = word.rstrip()
      if word in entries :
        continue

      count += 1
      if count > 10 :
        save (entries, "wikipedia_output.py", all_read = False)
        count = 0

      try :
        page = wiki_wiki.page(word)
        page.exists ()
      except :
        continue
      if page.exists():
        if page.summary.endswith (" refer to:") :
          text = page.text
        elif len (page.summary) > 200 :
          text = page.summary
        else :
          text = page.text[0:1000]
      else :
        print (word)
        wiktionary_entry = wiktionary.fetch(word)
        if not (wiktionary_entry and wiktionary_entry[0]["definitions"]
                and wiktionary_entry[0]["definitions"][0]["text"]):
          entries[word] = ("","","", False)
          text = ""
        else :
          text_list = []
          [text_list.extend(w["text"]) for w in wiktionary_entry[0]["definitions"]]
          reference = ""
          if all (      text_list[i].startswith("plural of ")
                     or text_list[i].find("indicative form of ") >= 0
                     or text_list[i].find("participle of ") >= 0
                   for i in range(1, len(text_list), 2)
                  ) :
            reference = text_list[1][text_list[1].rfind(' ')+1:]
          if reference :
            wiktionary_entry = wiktionary.fetch(reference)
            [text_list.extend(w["text"]) for w in wiktionary_entry[0]["definitions"]]
          text = '\n'.join(text_list)[0:1000]

      if text :
        lower = text.lower()
        language = guess_language(text, word, page.title, False)
        first = page.title
        first = ('' if word.lower() == page.title.lower()
                       else ("**" + first if not lower.find(word.lower()) >= 0
                             else first))
        #import pdb; pdb.set_trace()
        entries[word] = (first, language, text)
        print (word, entries[word])
  save (entries, "wikipedia_output.py", all_read = True)

by_language = {}
for word in entries :
  if len (sys.argv) >= 2 and word < sys.argv[1] :
    print ("skipping", word, flush=True)
    continue

  text = entries[word][2]
  full_text = False
  if len (text) < 60 and text.endswith (" refer to:") :
    print ("fetching", word)
    page = wiki_wiki.page(word)
    text = page.text
    full_text = True

  lower = text.lower()
  has_word = lower.find(word.lower()) >= 0
  if not has_word and not full_text and len(text) < 0 : # <0 to disable
    print ("Word missing.  Fetching", word, "Len", len(text))
    page = wiki_wiki.page(word)
    text = page.text
    lower = text.lower ()
    has_word = lower.find(word.lower()) >= 0

  lang = guess_language(text, word, entries[word][0], interactive=True,
                        default=entries[word][1], has_word=has_word)
  #if entries[word][1] and not lang == entries[word][1] :
  #  print (text)
  #  print (word, lang, entries[word][1], sep=" / ")
  #  pdb.set_trace ()
  lang_only = lang.split()[0] if lang else ""
  if lang :
    if not lang_only in by_language :
      by_language[lang_only] = []
    by_language[lang_only].append (word)

    first = entries[word][0]
    first = ('' if word.lower() == first.lower()
                   else ("**" + first if not has_word else first))
    entries[word] = (first, lang, text)

save (entries, "wikipedia_output.py")
