
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

words_neighbours_caps_1-1166.txt: words_classified_caps_1-1166.txt ./nearest_neighbours.c
	gcc -Wall -O2 nearest_neighbours.c -lbsd -o nearest_neighbours && ./nearest_neighbours $< > $@.part
	mv $@.part $@

words_likely_errs_caps_1-1166.txt: ./learn_errorness.py words_neighbours_caps_1-1166.txt
	./learn_errorness.py caps_1-1166 | grep -v "^[-!=]" >$@.part
	mv $@.part $@

trademarks.txt:
	zgrep '\\xc2\\xae' abstracts_1-1166.txt.gz | sed 's/.* \([^ ]*\)\\xc2\\xae.*/\1/; s/<sup>//g; s/<\/sup>//g; s/<b>//g; s/<\/b>//g; s/<i>//g; s/<\/i>//g; s/[[('"'"'"]//g' | grep '^[-A-Za-z]*$$' | sort -u > $@.part
	mv $@.part $@

proteins.txt:
	zcat abstracts_1-1166.txt.gz | grep " is a protein " | grep -v " is a protein coding gene" | sed 's/.*[" ]\([-A-Za-z0-9/().<>\\]*\) is a protein.*/\1/' | sed 's/.*[" ]\([-A-Za-z0-9/().<>\\]*\), [^.]*, is a protein.*/\1/' | sed "s/<i>//; s/<\/i>//; s/^(\(.*\))$$/\1/" | sort -u > proteins.txt

enzymes.txt:
	zcat abstracts_1-1166.txt.gz | grep " is an enzyme " | sed 's/.*[" ]\([-A-Za-z0-9/().<>\\]*\) is an enzyme.*/\1/' | sed 's/.*[" ]\([-A-Za-z0-9/().<>\\]*\), [^.]*, is an enzyme.*/\1/' | sed "s/<i>//; s/<\/i>//; s/^(\(.*\))$$/\1/" | sort -u > enzymes.txt

genes.txt:
	zcat abstracts_1-1166.txt.gz | grep " is a gene " | sed 's/.*[ "]\([-A-Za-z0-9/()<>_\\]*\) is a gene.*/\1/' | sed 's/.*[ "]\([-A-Za-z0-9/()<>_\\]*\), [^.]*, is a gene.*/\1/' | sed "s/<i>//; s/<\/i>//; s/^(\(.*\))$$/\1/" | sort -u > genes.txt

url_docs.txt:
	zgrep -i '\<\(http\)\|\(https\)|\(ftp\)\|\(www\)\|\(\<htm\>\)\|\(html\)\>' abstracts_1-1166.txt.gz | sed "s/ .*//" > $@.part
	zgrep -i '\.\(\(edu\>\)\|\(com\>\)\|\(org\>\)\|\(gov\>\)\|\(net\>\)\)' abstracts_1-1166.txt.gz | sed "s/ .*//" >> $@.part
	zgrep -i '\.\(\(ca\)\|\(it\)\|\(de\)\|\(dk\)\|\(nl\)\|\(ch\)\|\(fr\)\|\(uk\)\|\(au\)\)/' abstracts_1-1166.txt.gz | sed "s/ .*//" >> $@.part
	sort -u < $@.part > $@
	rm $@.part
