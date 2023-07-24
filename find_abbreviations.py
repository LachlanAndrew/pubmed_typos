#!/usr/bin/python

import sys
import gzip
import re

import pdb

def count_dict (a: dict, k) :
  end_dot = (k[-1] == '.')
  key = k[:-1] if end_dot else k

  if key not in a :
    a[key] = {False: 0, True: 0}

  a[key][end_dot] += 1

TLD = {"com", "edu", "gov", "org", "net", "ac", "ca", "fr", "de"}

def tidy_urls (url) :
  if type(url) == "str" :
    url = [url]

  # Trim excess
  url = [re.sub (r"(?:[-.\w]+\. +)+(www)", "www", p) for p in url]
  url = [re.sub (r"(.*)(?:\. [A-Z0-9]\w* *|\. *)$", r"\1", p) for p in url]
  url = [re.sub (r"(.*\.html?)-+\w\w+.strip()$", r"\1", p).strip() for p in url if "." in p]
  
  # Put in canonical form
  tidy_url = [re.sub("tp\W+www", "tp://www",
                     p.replace("approximately ", "~")
                      .replace(r"\xe2\x88\xbc", "~")
                      .replace(r"\xc5\xa9", "~")
                      .replace("/(/)", "//")
                      .replace("(/)/", "//")
                      .replace(r"\xc2\xbf\xc2\xbf", "//")
                      .replace("tp:@", "tp://")
                      .replace(" ", "")
                         )
              for p in url]

  return (url, tidy_url)

filename = sys.argv[1] if len(sys.argv) > 1 else "abstracts.txt.gz"

abbrev_re = re.compile(r"\w[\w.]*\.\w[\w.]*")
#url_re=re.compile(r"(?:(?:(?:http|https|ftp)[:;.l](?:/+|\(/\)/|/\(/\)|@|//@|/ /|\\xc2\\xbf\\xc2\\xbf)? *)?(?:[-\w]+@)?(?:(?:\w+[-\w]* *\. *)+\b(?:com|edu|gov|org|net|ac|ca|fr|de)\b(?:\. *\w+)?|(?:http\W*)?(?:www|ftp). *(?:[-\w]+\. *)*\w+)|(?:http|https|ftp)[:;.l] *(?:/+|\(/\)/|/\(/\)|@|//@|/ /|(?:\\xc2\\xbf)+) *(?:\w+@)?[-\w]+\. *[-\w.]+) *(?::\d+)? *(?:[/\\](?: *(?:approximately|~|\\xe2\\x88\\xbc) +)?(?:~ ?)?(?:[-\w.%#?+_/\\=]|&amp;)*)?|[-\w]+@(?:[-\w]+\.)+\w+|[-\w/]*/[-\w]*\.html?(?:[-\w.%#?+_/\\=]|&amp;)*\b")
url_re=re.compile(r"(?:(?:(?:http|https|ftp)[:;.l](?:/+|\(/\)/|/\(/\)|@|//@|/ /|\\xc2\\xbf\\xc2\\xbf)? *)?(?:[-\w]+@)?(?:(?:\w+[-\w]* *\. *)+\b(?:com|edu|gov|org|net|ac|ca|fr|de)\b(?:\. *\w+)?|(?:http\W*)?(?:www|ftp). *(?:[-\w]+\. *)*\w+)|(?:http|https|ftp)[:;.l] *(?:/+|\(/\)/|/\(/\)|@|//@|/ /|(?:\\xc2\\xbf)+) *(?:\w+@)?[-\w]+\. *[-\w.]+) *(?::\d+)? *(?:[/\\](?: *(?:approximately|~|\\xe2\\x88\\xbc) +)?(?:~ ?)?(?:[-\w.%#?+_/\\=]|&amp;)*)?|[-\w]+@(?:[-\w]+\.)+\w+|[-\w/]*/[-\w]*\.html?(?:[-\w.%#?+_/\\=]|&amp;)*\b")
new_url_re=re.compile(r"(?:(?:(?:http|https|ftp|html|www)[:;.l](?:/+|\(/\)/|/\(/\)|@|//@|/ /|\\xc2\\xbf\\xc2\\xbf)? *)?(?:[-\w]+@)?(?:(?:\w+[-\w]* *\. *)+\b(?:com|edu|gov|org|net|ac|ca|fr|de)\b(?:\. *\w+)?|(?:http\W*)?(?:www|ftp|doi:). *(?:[-\w]+\. *)*\w+)|(?:http|https|ftp)[:;.l] *(?:/+|\(/\)/|/\(/\)|@|//@|/ /|(?:\\xc2\\xbf)+) *(?:\w+@)?[-\w]+\. *[-\w.]+) *(?::\d+)? *(?:[/\\](?: *(?:approximately|~|\\xe2\\x88\\xbc) +)?(?:~ ?)?(?:[-\w.%#?+_/\\=]|&amp;)*)?|[-\w]+@(?:[-\w]+\.)+\w+|[-\w/]*/[-\w]*\.html?(?:[-\w.%#?+_/\\=]|&amp;)*\b")
other_url_re=re.compile(r"(?:http|www)[-:\w.%_/\\=@ ]+\b(?: *h *t *m *l?|com|org|net|edu)\b(?:\.\w+)*(?:[-\w/.]*\w)?(?:\?[-\w.%+_/\\=]*)?(?:#[-w.%+_/\\=]*)?")
abbrev_list = {}
end_sentence = {}
url = {}

trusted = 10000  # number of times a word must occur to be considered valid

# load frequencies of words from a previous run
word_count = {}
with open ("word_counts.txt", "r") as f :
  for line in f :
    line = line.split()
    word_count[line[0]] = sum([int(w) for w in line[1:]])
    if len (word_count) > 10000:
      break

count = 0
with (gzip.open (filename, "r") if filename.endswith(".gz") else open (filename, "rb")) as f :
  for line in f :
    if line.find(b" the ") == -1 :
      continue

    parts = line.strip().decode("utf-8").split('"')
    if len (parts) < 3 :
      new_parts = line.strip().decode("utf-8").split(",")
      try :
        year = int(new_parts[1][0:4])
        if year >= 1975 :
          try :
            parts = [",".join([new_parts[0], new_parts[1][0:4]]), "", new_parts[1][4:]]
          except :
            print (line)
            pdb.set_trace ()
          parts.extend (new_parts[2:])
        else :
          raise ValueError
      except ValueError :
        print ("Error", parts, file=sys.stderr)
        continue
    ID = parts[0] + '"' + parts[1].replace("”", '"') + '"'
    line = '"'.join(parts[2:])

    #print (simple_url_re.findall(line))
    old_line = line

    web_urls = url_re.findall(line)
    web_urls, w_tidy_urls = tidy_urls(web_urls)

    new_urls = new_url_re.findall(line) # TODO: strip (?:[\w.]* ) before "www"
    new_urls, n_tidy_urls = tidy_urls(new_urls)

    if False and web_urls != new_urls :
      print (line)
      print (web_urls)
      print (new_urls)
      pdb.set_trace ()
    if web_urls :
      print (line)
      for i in range(len(new_urls)) :
        #if (w_tidy_urls[i] != web_urls[i]) :
        #  print ("*", web_urls[i])
        #  print (" ", w_tidy_urls[i])
        #  pdb.set_trace ()
        pos = line.find(new_urls[i])
        pos_end = pos + len(new_urls[i])
        #if pos_end < len (line) :
        #  #next_end = line.find(" ", pos_end if line[pos_end] != " " else pos_end+1)
        #  #next_word = line[pos_end: next_end].rstrip().rstrip(".")
        #  if "/" in next_word or "." in next_word and not ('"' in next_word or ":" in next_word or "<" in next_word or ">" in next_word) :
        next_word = re.findall(" *(?:[-\w.%#?+_/\\=]|&amp;)*", line[pos_end:])
        if next_word :
          htm  = [i for i, w in enumerate(next_word) if w.find("htm")  != -1]
          http = [i for i, w in enumerate(next_word) if w.find("http") != -1]
          www  = [i for i, w in enumerate(next_word) if w.find("www")  != -1]
          if htm and (not http or htm[0] < http[0]) and (not www or htm[0] < www[0]) :
            more = "".join(next_word[0:htm[0]+1])
          else :
            htm = False
          #more.find("htm")
          # Allow spaces if a nearby htm[l]
          # Count double spaces as one, to match join above
          if htm  and line[pos_end:pos_end+len(more)] == more :
            next_word = more
          else :
            next_word = next_word[0]
        next_word = next_word.rstrip().rstrip(".")
        if ("/" in next_word or "." in next_word or "htm" in next_word) and new_urls[i].find("ftp.") == -1:
          print (new_urls[i])
          print (n_tidy_urls[i], new_urls[i].find("ftp."))

          new_urls[i] += next_word
          n_tidy_urls[i] += next_word.lstrip()

          print (new_urls[i])
          print (n_tidy_urls[i])
          #pdb.set_trace ()
        elif line[pos_end:].startswith(".") :   # avoid out-of-range err
          next_word = re.findall(". *(?:[-\w.%#?+_/\\=]|&amp;)*", line[pos_end:])
          if next_word :
            next_word = next_word[0]
          next_word = next_word.rstrip().rstrip(".")
          if next_word.find("htm") != -1 :
            print (new_urls[i])
            print (n_tidy_urls[i], new_urls[i].find("ftp."))
            new_urls[i] += next_word
            n_tidy_urls[i] += "." + next_word[1:].lstrip()
            print (new_urls[i])
            print (n_tidy_urls[i])
            #pdb.set_trace ()

        count_dict (url, new_urls[i])
        line = line.replace (new_urls[i], " ", 1)
      if line.find("www") != -1 or line.find("htm") != -1 or line.find("http") != -1 :
        other_urls = other_url_re.findall(old_line)

        print (old_line)
        print (new_urls)
        print (line.find("www"), line.find("htm"), line.find("http"))
        a = max(line.find("www"), line.find("htm"), line.find("http"))
        print (other_urls)
        print (line[max(0, a-10):min(len(line), a+20)])
        pdb.set_trace ()
      if count < 0:
        pdb.set_trace ()
    else :
      #print (line)
      #pdb.set_trace ()
      pass

    abbrevs = abbrev_re.findall(line)

    for m in abbrevs :
      parts = m.split(".")
      main = parts if parts[-1] else parts[:-1]

      try :
        [int(p) for p in main]
        continue        # ignore dot-separated numbers
      except ValueError :
        pass

      if (len(parts) == 2
          and   parts[0] in word_count
          and parts[0].islower()
          and ((((parts[1] in word_count and word_count[parts[1]] > trusted)
                 or (parts[1].lower() in word_count
                     and word_count[parts[1].lower()] > trusted))
                and parts[1][0].isupper()
                and (len(parts[1]) < 2 or parts[1][1:].islower()))
              or parts[1] in "23") ) :
        count_dict (end_sentence, m)
      elif (main[-1] in TLD
            or (main[0] == "ac" and len(main) == 2 and len (main[1]) == 2)
            or (len (main) > 2 and main[-2] in TLD)) :
        #count_dict(url, m)
        pass
      else :
        count_dict(abbrev_list, m)

      count += 1

for lst in (url, abbrev_list, end_sentence) :
  for w in sorted(lst, key = lambda w: -lst[w][True] - lst[w][False]) :
    print (w + "." if lst[w][True] > lst[w][False] else w,
           lst[w][True] + lst[w][False])
  print ("---")
