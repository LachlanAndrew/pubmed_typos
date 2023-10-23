
#LANGS  = en ar chem da de es fr in     it jp kr med nl pl zh oth
#LANGS1 = en    chem da de es fr hindi  it jp kr med nl pl zh oth

LANGS  = en chem med
LANGS1 = en chem med

#SOURCE = captial_words.txt
SOURCE = ../checked_words.txt

all: guessed_langs_1.txt

single_words:
	cat ../vocabulary/* | tr '_' '\012' | grep "^[a-z']*$$"  | sort -u > $@

#foreign: words_de.txt words_es.txt words_fr.txt words_id.txt words_it.txt words_jp.txt words_kr.txt words_nl.txt words_pl.txt words_yi.txt words_manual_ar.txt words_manual_slv.txt words_zh.txt
#	touch $@

wikipedia_output.py : wikipedia_input.txt
	./ask_wikipedia.py
	if grep -q 'all_read = False' $@; then touch $<; fi

word_models = $(LANGS:%=word_model_%.pkl)
guessed_langs.txt : $(word_models)
	./guess_lang.py -d -m word_model_ guess $(SOURCE) $(LANGS) > $@

word_models_1 = $(LANGS1:%=word_model_nodup_%.pkl)
guessed_langs_1.txt : $(word_models_1)
	./guess_lang.py -n 2 -d -m word_model_nodup_ guess $(SOURCE) $(LANGS) > $@

.PRECIOUS: wordlist_nodup_nosim_%.txt
wordlist_nodup_nosim_%.txt: wordlist_nodup_%.txt $(word_models_1)
	./guess_lang.py -m word_model_nodup_ guess $< $(LANGS) | grep " $* " | sed "s/ $* .*//" | sed "s/'s$$//" | sort -u > $@

#wordlist_nodup_nosim_pl.txt: wordlist_nodup_pl.txt
#	./guess_lang.py guess $< | ./ > $@

.PRECIOUS: word_model_%.pkl
word_model_%.pkl: wordlist_nodup_nosim_%.txt word_model_nodup_%.pkl
	./guess_lang.py -m word_model_ build $* wordlist_nodup_nosim_$*.txt

.PRECIOUS: word_model_nodup_%.pkl
word_model_nodup_%.pkl: wordlist_nodup_%.txt
	./guess_lang.py -m word_model_nodup_ build $* wordlist_nodup_$*.txt

# Word lists without words duplicated in any other list
# Set of languages is hard-coded in common_words.py
word_files = $(LANGS:%=words_%.txt)
.PRECIOUS: wordlist_nodup_%.txt
wordlist_nodup_%.txt : $(LANGS1:%=words_%.txt) $(LANGS1:%=words_manual_%.txt)
	#[ -f words_in.txt  ] || cp words_hindi.txt words_in.txt
	#[ -f words_ar.txt  ] || touch words_ar.txt
	#[ -f words_slv.txt ] || touch words_slv.txt
	./common_words.py $(LANGS1) > tmp_duplicates.txt

words_innames.txt : local_words_checked_1.txt
	grep "'indian'" local_words_checked_1.txt | sed "s/^'\([a-zA-Z]*\)'.*/\1/" > $@

words_in.txt : words_hindi_lists.txt words_innames.txt
	cat $^ | LC_all=C sort -u > $@

words_ar.txt : local_words_checked_1.txt words_manual_ar.txt
	(grep "'ar\(abic\)*'" local_words_checked_1.txt ; \
	        cat words_manual_ar.txt) | \
	    grep -v "'yes'" | \
	    sed "s/^'\([a-zA-Z]*\)'.*/\1/" | \
	    sort -u | \
	    grep -E -v '^(.|..|...|....)$$' | \
	    grep -E -v 'Quadzilla|*ation|Disney|Afgana|Afghanstan|Afghni|Afhgan|Canuckistan|Carl|[CK]h*ristan|Elbridge|Filmistan|Fulson|Gabe|Jihadistan|Londonistan|Pipelineistan|Rapistan|Richistan|Skateistan|Slackistan|Talibanistan|Wazristan|Youngistan' \
	    > $@

words_slv.txt : local_words_checked_1.txt words_manual_slv.txt
		#grep "'slv'" local_words_checked_1.txt | grep -v "'yes'"; \#
	(grep "'slavic'" local_words_checked_1.txt; \
		cat words_manual_slv.txt) | \
	    sed "s/^'\([a-zA-Z]*\)'.*/\1/" | \
	    sort -u | \
	    grep -E -v '^(.|..|...|....)$$' | \
	    grep -E -v 'Banff|Chipwich|Chowka|Darkh*|*zadeh|Falgun|Eskymo|Maidlow|Mashr|Muja|Musli|q[^u]|q$$|Namesnik|Ozekhome|Plotz|*bank|Senff|Serff|Shmul|Silkk|Soccer|*town' \
	    > $@

words_id.txt : words_indonesian.txt
	cp $< $@

words_hi.txt : words_hawaiian.txt
	cp $< $@

words_ma.txt : words_maori.txt
	cp $< $@

words_md.txt : words_medical.txt words_manual_md.txt
	(cat $< ; grep -v '^#' words_manual_md.txt) > $@

words_zh.txt : chinese.py
	#./chinese.py 2 > $@
	cp words_manual_zh.txt $@

words_kr.txt : chinese.py
	cp words_manual_kr.txt $@

words_jp.txt : $(SOURCE)
	(grep -E '(..ichi|..yama|..hiro)$$' $< | grep -v -i -E '(ovichi|ngwen)' ; grep -v '#' words_manual_jp | grep -v '*$$') | sort -u > $@

# Negative filter for Japanese words.  Misses  Ryo  and ts  words.
#grep -v '^[^AEIOUYS][^aeiouys]' < guessed_langs_1.txt | \
 grep -v '^[A-Za-z]*[^aeiousc][^aeiouy].* .* ' | \
 grep -v '[qQxXvV]' | \
 grep -v '[aeiou][aeiou]' | \
 grep '[aeiouy] .* '| \
 grep -v '[sc][^aeiouyh]' | \
 sort > words_maybe_jp_b.txt

words_oth.txt : $(SOURCE)
	cp $< $@

words_med_chem.txt: $(SOURCE) ../filter_select_medical.py
	../filter_select_medical.py < ../checked_words.txt > $@

words_med.txt: words_med_chem.txt
	grep "^1 " < $< | sed "s/.* //" > $@

words_chem.txt: words_med_chem.txt
	grep "^[a-z]" < $< > $@

local_words_checked.txt : $(word_models)
	# Keep word model from other, but ignore words actually in it
	mv words_oth.txt words_oth.txt.bak
	touch words_oth.txt
	./spelling.py $(SOURCE) -- $(LANG) > $@
	mv words_oth.txt.bak words_oth.txt

local_words_checked_1.txt : $(word_models_1)
	# Keep word model from other, but ignore words actually in it
	mv words_oth.txt words_oth.txt.bak
	touch words_oth.txt
	./spelling.py word_model_nodup_  $(SOURCE) -- $(LANG1) > $@
	mv words_oth.txt.bak words_oth.txt

.PRECIOUS: words_%.txt words_manual_%.txt
words_%.txt:
	gvim -c "set spelllang="$*  \
	     -c "spelld"            \
	     -c "g/[^A-Za-z]/d"     \
	     -c "%s/\/.*//"         \
	     -c "w! words_"$*".txt" \
	     -c "q" -c "q"
	touch words_manual_%.txt 
	cat words_manual_%.txt >> $@

words_manual_%.txt:
	touch words_manual_%.txt 

add_manual:
	for i in `echo $(LANGS) $(LANGS1) | tr ' ' '\012' | sort -u`; do     \
	  if [ -f words_$$i.txt -a words_manual_$$i.txt ] ; then	     \
	    cat words_$$i.txt words_manual_$$i.txt | sort -u > add_manual_tmp; \
	    mv add_manual_tmp words_$$i.txt;				     \
	  fi;								     \
	done

stats_1:
	echo "lang    =       ?       |       other lang";		\
	for a in $(LANGS); do						\
	  (echo $$a;							\
	   grep "=$$a" guessed_langs_1.txt | wc | awk '{print $$1}';	\
	   grep "$$a?" guessed_langs_1.txt | wc | awk '{print $$1}';	\
	   grep "$$a|" guessed_langs_1.txt | wc | awk '{print $$1}';	\
	   grep " $$a " guessed_langs_1.txt | wc | awk '{print $$1}') |	\
	  tr '\012' '\011';						\
	  echo;								\
	done
