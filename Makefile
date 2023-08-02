
all: words_classified_1-1166.txt words_neighbours_1-1166.txt words_likely_errs_1-1166.txt

words_hyphenated_1-1166.txt : words_1-1166.txt
	grep "^[a-z]*[a-z]-[a-z][a-z]* " $< | grep -v "[-].*-" > $@.part
	mv $@.part $@

words_classified_1-1166.txt : words_1-1166.txt likely_errors.py checked_words.txt known_errs.py
	./likely_errors.py > words_contradiction.txt

words_neighbours_1-1166.txt: words_classified_1-1166.txt ./nearest_neighbours.c
	gcc -Wall -O2 nearest_neighbours.c -lbsd -o nearest_neighbours && ./nearest_neighbours > $@.part
	mv $@.part $@

words_likely_errs_1-1166.txt: ./learn_errorness.py words_neighbours_1-1166.txt
	./learn_errorness.py | grep -v "^[-!=]" >$@.part
	mv $@.part $@
