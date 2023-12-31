#!/usr/bin/python

import sys

def include (word) :
  word = "^" + word.lower() + "$"
  stems = (
             ("ethyl", 5),
             ("acetyl", 5),
             ("aceto", 5),
             ("virus", 1),
             ("therap", 1),
             ("anaeseth", 1),
             ("aneseth", 1),
             ("athero", 1),
             ("bacter", 1),
             ("echino", 1),
             ("edema", 1),
             ("esopha", 1),
             ("gastr", 1, (("gastron", 0),)),
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
             ("somat", 1),
             ("sperm", 1),
             ("spora", 1),
             ("vira", 1),
             ("hexyl", 5),
             ("xylo", 1, (("xylophon", 0),)),
             ("ii$", 4, (("radii", 0), ("hawaii", 0))),
             ("trauma", 1),
             ("pharma", 1),
             ("zyg", 1),
             ("tomy", 1),
             ("diagnos", 1),
             ("lepto", 1, (("klepto", 0),)),
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
             ("pter", 1, (("adapter", 0), ("adopter", 0), ("chapter", 0), ("rupter", 0), ("prompter", 0), ("copter", 0))),
             ("skele", 1),
             ("pleur", 1),
             ("plexy", 1),
             ("cardi", 1, (("cardinal", 0),("carding", 0), ("cardigan",0))),
             ("cepha", 1),
             ("blasto", 1),
             ("toxi", 1, (("oxid", 5),)),
             ("plasty", 1),
             ("pneum", 1, (("pneumati", 0),)),
             ("phag", 1),
             ("ophth", 1),
             ("rhabd", 1),
             ("itis", 1, (("british", 0),)),
             ("osis", 1),
             ("ococc", 4),
             ("acea", 4),
             ("actino", 1),
             ("assay", 1),
             ("campyl", 1),
             ("cyt", 1, (("scyth", 0),)),
             ("derm", 1, (("alderm", 0),("underm", 0))),
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
             ("oncol", 1, (("noncol", 0),)),
             ("olog", 1, (("antholog", 0),
                          ("anthropolog", 0),
                          ("anthropomorpholog", 0),
                          ("archaeolog", 0),
                          ("archeolog", 0),
                          ("assyri", 0),
                          ("autolog", 0),
                          ("chronolog", 0),
                          ("cosmetolog", 0),
                          ("cosmolog", 0),
                          ("criminolog", 0),
                          ("demonolog", 0),
                          ("doxolog", 0),
                          ("ecclesiolog", 0),
                          ("egypt", 0),
                          ("epistolog", 0),
                          ("eschatolog", 0),
                          ("ethnolog", 0),
                          ("etymolog", 0),
                          ("geolog", 0),
                          ("historiolog", 0),
                          ("holog", 0),
                          ("hydrolog", 0),
                          ("ideolog", 0),
                          ("lexicolog", 0),
                          ("liturgolog", 0),
                          ("menolog", 0),
                          ("meteorolog", 0),
                          ("methodolog", 0),
                          ("monolog", 0),
                          ("musicolog", 0),
                          ("mytholog", 0),
                          ("neolog", 0),
                          ("oenolog", 0),
                          ("osmolog", 0),
                          ("patrolog", 0),
                          ("penolog", 0),
                          ("petrolog", 0),
                          ("philolog", 0),
                          ("prolog", 0),
                          ("psepholog", 0),
                          ("pyrolog", 0),
                          ("scientolog", 0),
                          ("seismolog", 0),
                          ("seminolog", 0),
                          ("sociolog", 0),
                          ("spectrolog", 0),
                          ("syphilolog", 0),
                          ("systematolog", 0),
                          ("terminolog", 0),
                          ("theolog", 0),
                          ("typolog", 0),
                          ("ufolog", 0),
                          ("technolog", 0, (("bio", 1),
                                            ("nano", 1),
                                            ("agro", 1),
                                            ("histo", 1),
                                            ("neuro", 1),
                                            ("cyto", 1),
                                          ),
                                         ),
                         ),
                        ),
             ("opto", 1),
             ("pathy", 1),
             ("phyl", 1),
             ("plasm", 1),
             ("spori", 1),
             ("zoo", 1, (("zoom", 0), )),
             ("uter", 1, (("neuter", 0), ("puter", 0),("couter", 0))),
             ("acanth", 1),
             ("oxy", 5),
             ("benz", 5),
             ("acryl", 5),
             ("alk", 5, (("walk", 0), ("talk", 0))),
             ("phosph", 5),
             ("pheno", 1),
             ("chol", 1, (("schol", 0),("echolocat", 0))),
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
                       ("xyl", 1, (("xylyl", 5), ("xylen", 5))),
                       ("cylind", 1, (("cylinder", 0),)),
                       ("argyll", 3),
                       )),
             ("acryl", 5),
             ("benz", 5),
             ("bromo", 5),
             ("chlor", 5),
             ("iodi", 5),
             ("oxid", 5),
             ("oxy", 5),
             ("phosph", 5),
             ("sulf", 5),
             ("nitr", 5),
             ("propan", 5),
             ("amino", 5),
             ("amine", 5, (("examine", 0), )),
             ("acetal", 5),
             ("acyclo", 5),

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
             ("zumab", 1),

             ("ithecus", 4),
             ("formis", 4),
             ("iform", 4, (("uniform", 0), )),
             ("ensis$", 4),
             ("morph$",  4, (("endomorph", 1), ("ectomorph", 1))),
             ("morphs$", 4, (("endomorph", 1), ("ectomorph", 1))),
             ("morpha$", 4),
             ("anthus", 4),

             ("fluor", 5, (("fluoresc", 0),)),

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
        print (5, "       yl", name)
