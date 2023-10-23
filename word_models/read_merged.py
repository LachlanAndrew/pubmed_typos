import pdb

class read_merged :
  handles = {}
  heads = {}
  keys = {}

  def read_next_else_True (self, lang) :
    #if lang in self.heads :  print ("was", self.heads[lang], len (self.heads[lang]))
    self.heads[lang] = self.handles[lang].readline()
    #print ("\t", lang, self.heads[lang].rstrip(), len (self.heads[lang]))
    if len (self.heads[lang]) == 0 :
      #pdb.set_trace ()
      self.handles[lang].close()
      if lang in self.handles: del self.handles[lang]
      if lang in self.heads:   del self.heads[lang]
      if lang in self.keys:    del self.keys[lang]
      return True

    self.keys[lang] = self.key (self.heads[lang])

    return False


  def __init__(self, files, key = lambda x:x, ignore_missing = False) :
    self.key = key

    missing = []
    for f in files :
      if isinstance(files[f],str) :
        try :
            self.handles[f] = open (files[f], "r")
        except FileNotFoundError :
            if ignore_missing :
              missing.append(files[f])
              continue
            else :
              raise
      else :
        self.handles[f] = files[f]

      self.read_next_else_True (f)

    self.files = [f for f in files if not f in missing]
        
  def next (self, tell_origin=False, merge_duplicates=False) :
    if not self.heads :
      return (None, None) if tell_origin else None

    head_file = min(self.keys, key= lambda x : self.keys[x])
    retval = self.heads[head_file]
    if merge_duplicates :
      origin = [h for h in self.heads if self.heads[h] == retval]

      extra_origin = []
      for f in origin :
        if not self.read_next_else_True (f) :
          while self.heads[f] == retval :
            extra_origin.append (f)

            if self.read_next_else_True (f) :
              break

      origin.extend (extra_origin)
    else :
      origin = head_file
      self.read_next_else_True (head_file)

    if tell_origin :
      return retval, origin
    else :
      return retval

  def close (self) :
    for f in self.handles :
      self.handles[f].close()
