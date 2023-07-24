#!/usr/bin/python

import gzip
import sys
import pdb

sgml_tags = {
  "amp": "&",
  "lt": "<",
  "gt": ">",
}

def de_sgml (line) :
  parts = line.split("&")
  if len(parts) == 1 :
    return line

  for i, s in enumerate (parts) :
    if i > 1 :
      tag_end = s.find(";")
      if tag_end == -1 :
        print ("mal-formed SGML tag", s, file=sys.stderr)
        continue

      tag = s[0:tag_end]
      if tag not in sgml_tags :
        print ("Unknown SGMP tag &%s;" % tag, file=sys.stderr)
        print ("Line:", line, file=sys.stderr)
        exit()
      else :
        parts[i] = sgml_tags[tag] + s[tag_end+1:]

  return "".join (parts)

fields = {
  b"AbstractText",
  b'ArticleId IdType="doi"',
  b'PMID',
  b"Title",      # journal title
  b"Volume",
  b"Issue",
  b"ArticleTitle",
  b"MedlinePgn",
  b"Year",      # multiple years.  We want pub year
}

#abs_range = (1,4)
abs_range = (1, 1166)
#abs_range = (1008, 1009)
outfile_name = "abstracts_%d-%d.txt.gz" % abs_range
with gzip.open (outfile_name, "wb") as outfile :
  for i in range (abs_range[0], abs_range[1]+1) :
    filename = "ftp.ncbi.nlm.nih.gov/pubmed23n%04d.xml.gz" % i
    print (filename, end="\r")
    try :
      with gzip.open (filename, "r") as f :
        date = ""
        for line in f :
          tag = line[line.find(b"<")+1:line.find(b">")]
          if tag == b"PubmedArticle" :
            entry = {field:"" for field in fields}
            #abstract = None
            #PMID = None
            #doi = None
            #journal_name = None
            #journal_volume = None
            #journal_issue = None
            #article_title = None
          elif tag == b"/PubmedArticle" :
            if entry[b"AbstractText"] :
              articleID = []

              PMID = entry[b'PMID']
              title = entry[b"Title"]
              volume = [entry[b"Volume"]]
              if not PMID or not title or not volume :
                print ("Error:", entry, file=sys.stderr)
              else :
                articleID.append (PMID)
                articleID.append (title)

              if entry[b"Issue"] :
                volume.extend(("(", entry[b"Issue"], ")"))
              if entry[b"MedlinePgn"] :
                volume.extend((":", entry[b"MedlinePgn"]))
              if entry[b"Year"] :
                volume.extend((",", entry[b"Year"]))
              articleID.append("".join(volume))
              
              if entry[b"ArticleTitle"] :
                # Replace double quotes by unicode to aide parsing
                # (Original unicode is escaped)
                title = entry[b"ArticleTitle"].replace('"', '”')
                articleID.append("".join(('"', title, '"')))

              outfile.write (b"".join([(" ".join(articleID)).encode(), b" ", entry[b"AbstractText"].encode(), b"\n"]))
              if any ([ord(a) >= 128 for a in entry[b"AbstractText"]]) :
                print ("Non-ASCII", PMID, file=sys.stderr)

          elif tag.find(b"Date") != -1 :
            date = tag
          else :
            # Better: Find first tag on the line, and see what it is
            if tag.startswith(b"PMID") :
              version = "v"+chr(tag[-2])
              tag = b"PMID"
            else :
              version = ""
            if tag in fields :
              #for tag in fields :
              #  pos = line.find (b"<" + tag)
              #  if pos != -1 :
              if tag != b"Year" or date == b"PubDate" :
                contents = str(line)
                entry[tag] = contents[contents.find(">")+1:contents.rfind("<")]+version
            elif tag.startswith(b"PMID") :
              print ("Unknown PMID format", line.strip())
            #abst = line.find (b"<AbstractText>")
            #if abst != -1 :
            #  line = str(line)
            #  line = line[abst + len("<AbstractText>")+2:-(len("</AbstractText>\n")+2)]
            #  abstract = de_sgml(line)
            #  #print (abstract)
            #else :
            #  doi_pos = line.find(b'<ArticleId IdType="doi">')
            #  if doi_pos != -1 :
            #    doi = str(line)
            #    doi = doi[doi_pos + len('<ArticleId IdType="doi">')+2:-(len("</ArticleId>")+3)]
            #    #print (doi)

    except EOFError :
      print ("Unexpected EOF in", filename, file=sys.stderr)
    except FileNotFoundError :
      print ("File", filename, "not found", file=sys.stderr)
