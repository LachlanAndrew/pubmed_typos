To identify valid words from a domain, embedded in a base language (English)

Procedure:
* Find list of words with frequencies
* Create spell checker dictionary of words with frequency above a threshold
* For all words with a frequency above a threshold theta
  - Build list P of the word and spell-checker correction for the word
    (if not in list of known errors from the base language)
  These will be used to see common similar words that are not errors
* For all words with frequency below theta
  - Build list U of the word and spell-checker correction for the word
  These will be classified into correct words and typos
* For spelling errors from the base language
  - Build list E of the word and spell-checker correction for the word

* For all spelling corrections in E that contain a space
  - if the space-separated phrase (or dash-separated phrase)
        occurs at least 30 times as often as the word
    Add list D of detected errors

* Train a (soft) classifier to distinguish between P and E.
* Classify words in U
  - words clearly classified as P are taken as proper words: add to lexicon L
  - words clearly classified as E are taken as errors: add to D
  - words not clearly classified can be ignored.
  Thresholds can depend on the frequency of the word: more common=> more P

* Count occurrences of errors (in D) by journal
* Empty L and repeat the above for only those words that are:
  (a) from a journal where (number of articles)/(0.1+number of errors) > 100
      (i.e., at least 10 articles, and at least 100 if there is an error)
  (b) not from articles with errors
  with different thresholds for "clearly classified", more likely to declare P



Ways to distinguish typos from new words:
* intra-word black-box model
  - score each word
  - score perturbations of words
  ? expand alphabet with morphemes http://morpho.aalto.fi/projects/morpho/
    https://ufal.mff.cuni.cz/~hana/teaching/2011su-morph/creutz-lagus-2007.pdf
* Cluster words with a distance based on the difference from known word
* Language model: next/previous word, KS distance between contexts
* Language model: weighted bag of words
* proximity to other unknown words.  Latin words, author names, foreign words and journal name abbreviations often appear in clusters.

* Features:
  - frequency of word
  - frequency of replacement
  - closeness of error
  - is journal OCR'd?
  - reliability of journal
  - Is work known foreign word near other foreign words?

Learn names from authors in PubMed.

Detect units/abbreviations by being before/after a number.

Trusted words:
* Fraction  f  such that at most fraction f of the words occur at least 1/f times.
* Remove known words



CLASSIFYING ERRORS
==================
OCR errors:
i/l t/l c/o c/e y/v h/n h/b r/n g/q u/n
O/C O/Q I/E H/M
I/l I/t J/l J/d L/l L/h L/b
m/rn H/ll

typing errors:
  fat-finger errors:
  transposition errors:
  missed letters
  habit errors (e.g, "g" after "in")

spelling errors
- double letters
- vowel interchange
- consonant interchange
- inserted letter
- removed letter

(O,F,X,M,H,D,V,C,I,R)
