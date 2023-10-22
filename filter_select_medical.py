#!/usr/bin/python

import sys

def include (word) :
  word = "^" + word.lower() + "$"
  stems = (
             ("ethyl", 2),
             ("acetyl", 2),
             ("aceto", 2),
             ("virus", 1),
             ("therap", 1),
             ("anaeseth", 1),
             ("aneseth", 1),
             ("athero", 1),
             ("bacter", 1),
             ("echino", 1),
             ("edema", 1),
             ("esopha", 1),
             ("gastr", 1),
             ("gland", 1, (("ngland", 0),)),
             ("hepat", 1),
             ("ichthy", 1),
             ("immun", 1),
             ("crani", 1),
             ("karyo", 1),
             ("lymph", 1),
             ("odont", 1),
             ("oedem", 1),
             ("pancrea", 1),
             ("protein", 1),
             ("respir", 1),
             ("rhiz", 1),
             ("phyt", 1),
             ("plagi", 1),
             ("sperm", 1),
             ("spora", 1),
             ("vira", 1),
             ("xylo", 1),
             ("trauma", 1),
             ("pharma", 1),
             ("zyg", 1),
             ("tomy", 1),
             ("diagnos", 1),
             ("lepto", 1),
             ("megaly", 1),
             ("mening", 1),
             ("metabo", 1),
             ("haem", 1),
             ("hemo", 1),
             ("lepido", 1),
             ("laparo", 1),
             ("folia", 1),
             ("eryth", 1),
             ("dactyl", 1),
             ("cirrho", 1),
             ("brachy", 1),
             ("bronch", 1),
             ("angio", 1),
             ("pter", 1),
             ("skele", 1),
             ("pleur", 1),
             ("plexy", 1),
             ("cardi", 1, (("cardinal", 0),)),
             ("cepha", 1),
             ("blasto", 1),
             ("toxi", 1, (("oxid", 2),)),
             ("plasty", 1),
             ("pneum", 1),
             ("phag", 1),
             ("ophth", 1),
             ("oncol", 1),
             ("rhabd", 1),
             ("itis", 1, (("british", 0),)),
             ("ococc", 4),
             ("acea", 4),
             ("actino", 1),
             ("assay", 1),
             ("campyl", 1),
             ("cyt", 1, (("scyth", 0),)),
             ("derm", 1, (("alderm", 0),)),
             ("entero", 1),
             ("fibro", 1),
             ("globuli", 1),
             ("idae", 1),
             ("leuco", 1),
             ("leuko", 1),
             ("myc", 1),
             ("myo", 1),
             ("bibli", 0),
             ("apolog", 0),
             ("astro", 0),
             ("olog", 1, (("antholog", 0),
                          ("archaeolog", 0),
                          ("archeolog", 0),
                          ("egypt", 0),
                          ("assyri", 0),
                          ("chronolog", 0),
                          ("cosmolog", 0),
                          ("criminolog", 0),
                          ("demonolog", 0),
                          ("mytholog", 0),
                          ("doxolog", 0),
                          ("ecclesiolog", 0),
                          ("eschatolog", 0),
                          ("musicolog", 0),
                          ("geolog", 0),
                          ("ideolog", 0),
                          ("lexicolog", 0),
                          ("liturgolog", 0),
                          ("methodolog", 0),
                          ("petrolog", 0),
                          ("pyrolog", 0),
                          ("scientolog", 0),
                          ("seismolog", 0),
                          ("sociolog", 0),
                          ("technolog", 0, (("bio", 1),
                                            ("nano", 1),
                                            ("agro", 1),
                                            ("histo", 1),
                                            ("neuro", 1),
                                            ("cyto", 1),
                                          ),
                                         ),
                          ("terminolog", 0),
                          ("theolog", 0),
                          ("typolog", 0),
                         ),
                        ),
             ("opto", 1),
             ("osis", 1),
             ("pathy", 1),
             ("phyl", 1),
             ("plasm", 1),
             ("spori", 1),
             ("zoo", 1),
             ("uter", 1, (("puter", 0),("couter", 0))),
             ("acanth", 1),
             ("oxy", 2),
             ("benz", 2),
             ("acryl", 2),
             ("alk", 2),
             ("phosph", 2),
             ("pheno", 1),
             ("chol", 1),
             ("lacto", 1),
             ("galact", 1),
             ("yl", 2, (
                       ("skyl", 0),
                       ("ceylon", 0),
                       ("sylv", 0),
                       ("gyl", 3, (("strongyl", 1),
                                   ("propargyl", 1),
                                   ("gongyl", 1))),
                       ("campyl", 1),
                       ("chyli", 1),
                       ("conchyl", 1),
                       ("condyl", 1),
                       ("cordyl", 1),
                       ("cotyl", 1),
                       ("crocodyl", 1),
                       ("pachyl", 1),
                       ("platyl", 1),
                       ("strongyl", 1),
                       ("phyl", 1),
                       ("psyll", 1),
                       ("amphi", 1),
                       ("gongyl", 0),
                       ("gryllo", 0),
                       ("style", 0),
                       ("styli", 0),
                       ("stylo", 0),
                       ("syll", 0),
                       ("sylph", 0),
                       ("taylor", 0),
                       ("ylike", 0),
                       ("zeylan", 0),
                       ("bury", 0),
                       ("maryl", 0, (("amaryl", 1),)),
                       ("xyl", 0, (("hexyl", 2),)),
                       ("cylind", 1, (("cylinder", 0),)),
                       ("argyll", 3),
                       )),
             ("acryl", 2),
             ("alk", 2),
             ("benz", 2),
             ("bromo", 2),
             ("chlor", 2),
             ("iodi", 2),
             ("oxid", 2),
             ("oxy", 2),
             ("phosph", 2),
             ("sulf", 2),
             ("nitr", 2),
             ("propan", 2),
             ("amino", 2),
             ("amine", 2),
             ("acetal", 2),
             ("acyclo", 2),

             ("ularis", 1),
             ("abdom", 1),
             ("opsis", 1, (("synops", 0),)),
             ("opses", 1, (("synops", 0),)),
             ("cauda", 1),
             ("cerato", 1),
             ("acidi", 1),
             ("aculea", 1),
             ("agrost", 1),
             ("albi", 1),
             ("dors", 1, (("adors", 0),
                          ("corridors", 0),
                          ("endors", 0),
                          ("indors", 0),
                          ("dorset", 0),
                          ("vendors", 0),
                          ("tudors", 0),
                          )),

             ("ithecus", 4),
             ("formis", 4),
             ("iform", 4),
             ("ii", 4, (("radii", 0), ("skiing", 0))),
             ("morph", 4),
             ("anthus", 3),

          )

  retval = None
  s = stems
  while s :
    recur = False
    for stem in s :
      if word.find(stem[0]) >= 0 :
        if len (stem) == 2 :
          return stem[0:2]
        else :
          retval = stem[0:2]
          s = stem[2]
          recur = True
          break
    if not recur :
      break

  return retval if retval else ("", 0)


def exclude (word) :
  for stem in (
              "cardinal",
              ) :
      if word.find(stem) >= 0 :
        return True

  return False

organics = {}

for line in sys.stdin :
  if len (line) >= 6 :
    line = line[0:-1]
    stem = include (line)
    if (stem[0]) :
      if stem[1] == 2 :
        prefix = line[0:6]
        if prefix not in organics :
          organics[prefix] = []
        organics[prefix].append(line)
      else :
        print ("%d %10s %s" % (stem[1], stem[0], line))

for i in organics :
  if len (organics[i]) > 5 :
    for name in organics[i] :
      if not exclude (name) :
        print (name)
