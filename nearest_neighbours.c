#include <stdio.h>
#include <stdlib.h>
#include <bsd/string.h>
#include <stdbool.h>

#define context 4
typedef struct diff {
    char type; // *,/ (un)double, X transpose, +,- add/drop, R replace
    char change[2];
    char context_after[context];
    char context_before[context];
} diff;

typedef struct ngbr {
    long index;
    int closeness;
    char type;  // + (valid word), * (error), ? (no idea) _ (space separated)
} ngbr;

// Return true if a space-terminated string is all lower case ASCII
bool
is_lower(const char *str)
{
    while (*str >= 'a' && *str <= 'z')
        str++;
    return *str == '\0';
}

// Find the difference between two strings a, b that differ in one of six ways:
// * A letter in a can be doubled in b
// / A double letter in a can become single in a
// X Two adjacent letters can be transposed,
// + A letter or space can be added in b
// - A letter in a can be dropped
// R A letter in a can be replaced by another in b.
void
find_diff (char *a, char *b, diff *d)
{
    int len_a = strlen(a);
    int len_b = strlen(b);
    int min_len = len_a < len_b ? len_a : len_b;
    int i, err_pos1;
    char *err_pos2;

    for (i = 0; i < min_len && a[i] == b[i]; i++)
        ;
    err_pos1 = i;
    if (len_a == len_b) {       // Transpose or replace
        d->change[0] = a[i];
        d->change[1] = b[i];
        if (i+1 == len_a || a[i+1] == b[i+1]) {
            if (i > 0 && ((a[i] == a[i+1] && b[i] == b[i-1])
                      || ( a[i] == a[i-1] && b[i] == b[i+1]))) {
                d->type = '#';  // double wrong letter
                err_pos2 = a+err_pos1 + 2;
            } else {
                d->type = 'R';
                err_pos2 = a+err_pos1 + 1;
            }
        } else if (i+1 < len_a && a[i+1] == b[i] && a[i] == b[i+1]) {
            d->type = 'X';
            err_pos2 = a+err_pos1+2;
        } else {
            d->type = 'R'; // two letter substitution by affix rules
            err_pos2 = a+err_pos1 + 2;
        }
    } else if (len_a > len_b) {
        err_pos2 = b+err_pos1;
        d->change[0] = a[i];
        d->change[1] = 0;
        if (i > 0 && a[i-1] == a[i]) {
            d->type = '*';
        } else {
            d->type = '+';
        }
    } else {
        err_pos2 = a+err_pos1;
        d->change[0] = b[i];
        d->change[1] = 0;
        if (i > 0 && b[i-1] == b[i]) {
            d->type = '/';
        } else {
            d->type = '-';
        }
    }
    strlcpy(d->context_after, err_pos2, sizeof(d->context_after));
    //fprintf(stderr, "err_pos2 %ld %x %ld %d\n", err_pos2 - a, err_pos2[1], err_pos2 - b, i);
    char *dcb = d->context_before;
    int j;
    for (j = 0, i--; i >= 0 && j < sizeof(d->context_before); i--, j++) {
        //fprintf (stderr, "i %d j %d chr %c %d\n", i, j, a[i], a[i]);
        *(dcb++) = a[i];
    }
    if (i == 0)
        *dcb = '\0';

    /*
    fprintf (stderr, "change_%s_%s_%c_%c%c_",
             a, b, d->type, d->change[0], d->change[1]);
    for (i = 0; i < sizeof(d->context_before) && d->context_before[i]; i++)
        fprintf (stderr, "%c", d->context_before[i]);
    fprintf (stderr, "_");
    for (i = 0; i < sizeof(d->context_after) && d->context_after[i]; i++)
        fprintf (stderr, "%c", d->context_after[i]);
    fprintf (stderr, "\n");
    */
}

// Returns a score of how similar difference ("error") a is to b.
// This is based on the type of error and the amount of shared context
int
diff_closeness (diff *a, diff *b)
{
    int closeness = 6;
    bool close_type = ((a->type == 'R' && b->type == '#')
                    || (a->type == '#' && b->type == 'R'));

    if (a->type != b->type && !close_type)
        return 0;               // TODO be more nuanced

    if (close_type)
        closeness--;

    if (a->change[0] != b->change[0] && a->change[1] != b->change[1])
        return closeness/4;     // TODO be more nuanced

    if (a->change[0] != b->change[0] || a->change[1] != b->change[1])
        return closeness/2;     // TODO be more nuanced

    int i;
    for (i = 0; i < sizeof(a->context_after) && a->context_after[i] == b->context_after[i]; i++)
        ;
    closeness += i;
    
    for (i = 0; i < sizeof(a->context_before) && a->context_before[i] == b->context_before[i]; i++)
        ;
    closeness += i;

    return closeness;
}

// Returns >0 if  n  is preferable to (closeness, type),
// either because it is a + or - rather than ?, or because it is closer
int priority (ngbr* n, char type, int closeness) {
    if (closeness == 0) {
        //fprintf (stderr, "close=0\n");
        return -1;
    }

    int t1 = (n->type == '?' || n->type == '\0');
    int t2 = (   type == '?');

    if (t1 != t2) {
        //fprintf (stderr, "t1 %d t2 %d (closeness %d)\n", t1, t2, closeness);
        return t1 - t2;
    } else {
        //fprintf (stderr, "n->closeness %d closeness %d\n", n->closeness, closeness);
        return closeness - n->closeness;
    }
}

int
main (int argc, char *argv[])
{
    //long int word_count = 726578;
    //long int char_count = 15514305;
    long int word_count = 500000;
    long int char_count = 22000000;
    const int buf_len = 200;
    char *data = (char*)malloc(char_count + 2*word_count + buf_len); // string+type+\0
    diff *diffs = (diff*)malloc(word_count * sizeof(diff));

    int ngbr_count = 10;
    ngbr **neighbours = (ngbr**)malloc(word_count * sizeof(ngbr*));
    ngbr *ngbr_data = (ngbr*)malloc(word_count * ngbr_count * sizeof(ngbr));

    char *words[word_count];
    FILE * fp;

    int i;

    if (!data || !diffs || !neighbours || !ngbr_data) {
        fprintf (stderr, "Failed to allocate memory\n");
        exit(1);
    }

    // Set up 2D array of neighbours
    for (i = 0; i < word_count; i++)
        neighbours[i] = ngbr_data + i*ngbr_count;

    if ((fp = fopen ("words_classified_1-1166.txt", "r")) == NULL) {
        fprintf (stderr, "Could not open file for reading\n");
        exit(1);
    }

    // Read words to check into words
    // Create diff between word to check and its "correction", in diffs
    char *curr = data;
    int max_iter = 800000;
    for (i = 0; i < word_count; ) {
        if (!fgets(curr, buf_len, fp)) {
            word_count = i;
            break;
        }
        char *end1 = strchr(curr+1, ' ');       // ignore leading +,?,*,_
        if (!end1)
            continue;
        char *end2 = strchr(end1+1, ' ');
        if (!end2)
            continue;
        *end1 = *end2 = '\0';
        //fprintf (stderr, "end1 %ld %s end2 %ld %s\n",
        //         end1 - curr, curr, end2 - curr, end1+1);
        if (is_lower(curr+1)) {
            words[i] = curr+1;
            curr = end1+1;
            find_diff (words[i], end1+1, diffs+i);
            i++;
            if (!--max_iter) {
                word_count = i;
                fprintf (stderr, "Stopping after %d\n", i);
                break;
            }
        }
    }

    // Find ngbr_count nearest neighbours to each word
    for (i = 0; i < word_count-1; i++) {
        int j;
        
        for (j = i+1; j < word_count; j++) {
            int d = diff_closeness(diffs+i, diffs+j);
            if (d == 0)
                continue;
            bool track_insert = false;
            if (!strcmp(words[j], "xyzapoendix")) {
                fprintf (stderr, "dist %s (%d %c %c%c) to %s (%d %c %c%c) is %d\n", words[i], i, diffs[i].type, diffs[i].change[0], diffs[i].change[1], words[j], j, diffs[j].type, diffs[j].change[0], diffs[j].change[1], d);
                track_insert = true;
            }
            int k = i;
            for (int n = 0; n < 2; n++) {
                char type = words[i+j-k][-1];       // * err, + valid, ? unknown
                // insert d as a possible neighbour of k
                int m;
                for (m = ngbr_count-1; m > 0; m--) {
                    //if (neighbours[k][m-1].closeness < d &&
                    //        (type != '?' || neighbours[k][m-1].type == '?'
                    //                     || neighbours[k][m-1].type == '\0')) {
                    //fprintf (stderr, "%s %s: ", words[k], words[neighbours[k][m-1].index]);
                    if (priority(&(neighbours[k][m-1]), type, d) > 0) {
                        if (track_insert && neighbours[k][m-1].closeness)
                            fprintf (stderr, "Moving %s %ld for %s m %d\n", words[neighbours[k][m-1].index], neighbours[k][m-1].index, words[i+j-k], m);
                        neighbours[k][m] = neighbours[k][m-1];
                    } else {
                        if (track_insert)
                            fprintf (stderr, "breaking: ngbr %s d %d new d %d type %c their type %c i= %d j %d k %d\n", words[neighbours[k][m-1].index], neighbours[k][m-1].closeness, d, type, neighbours[k][m-1].type, i, j, k);
                        break;
                    }
                }
                if (m < ngbr_count-1) {
                    neighbours[k][m].closeness = d;
                    neighbours[k][m].index = (i+j)-k;
                    neighbours[k][m].type = words[i+j-k][-1];

                    if (track_insert) {
                        fprintf (stderr, "Inserting %s %d (%c %c%c) %d d %d m %d i %d j %d k %d\n", words[i+j-k], i+j-k, diffs[i+j-k].type, diffs[i+j-k].change[0], diffs[i+j-k].change[1], neighbours[k][m].closeness, d, m, i, j, k);
                        fprintf (stderr, "%s %d", words[k]-1, k);
                        int a;
                        for (a = 0; a < ngbr_count; a++) {
                            fprintf (stderr, " %c%ld_%d", neighbours[k][a].type, neighbours[k][a].index, neighbours[k][a].closeness);
                        }
                        fprintf (stderr, "\n");
                    }
                }
                k = j;
            }
        }
    }
    //fprintf (stderr, " %ld, %d\n", word_count, max_iter);
    

    for (i = 0; i < word_count; i++) {
        int j;
        int type_count [7] = {0,0,0,0,0,0,0};
        printf ("%s %d", words[i]-1, i);
        for (j = 0; j < ngbr_count; j++) {
            if (neighbours[i][j].closeness)
                switch (words[neighbours[i][j].index][-1]) {
                    case '?': type_count[0]++; break;
                    case '-': type_count[1]++; break;
                    case '*': type_count[2]++; break;
                    case '_': type_count[3]++; break;
                    case '+': type_count[4]++; break;
                    case '!': type_count[5]++; break;
                    case '=': type_count[6]++; break;
                }
            printf (" %c%ld_%d", neighbours[i][j].type, neighbours[i][j].index, neighbours[i][j].closeness);
        }
        for (j = 0; j < sizeof(type_count)/sizeof(*type_count); j++)
          printf (" %d", type_count[j]);
        printf (" %c\n", diffs[i].type);
    }
}
