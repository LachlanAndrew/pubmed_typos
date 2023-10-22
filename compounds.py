#!/usr/bin/python

import sys

elements = {
    "H",
    "He",
    "Li",
    "Be",
    "B",
    "C",
    "N",
    "O",
    "F",
    "Ne",
    "Na",
    "Mg",
    "Al",
    "Si",
    "P",
    "S",
    "Cl",
    "Ar",
    "K",
    "Ca",
    "Sc",
    "Ti",
    "V",
    "Cr",
    "Mn",
    "Fe",
    "Co",
    "Ni",
    "Cu",
    "Zn",
    "Ga",
    "Ge",
    "As",
    "Se",
    "Br",
    "Kr",
    "Rb",
    "Sr",
    "Y",
    "Zr",
    "Nb",
    "Mo",
    "Tc",
    "Ru",
    "Rh",
    "Pd",
    "Ag",
    "Cd",
    "In",
    "Sn",
    "Sb",
    "Te",
    "I",
    "Xe",
    "Cs",
    "Ba",
    "La",
    "Ce",
    "Pr",
    "Nd",
    "Pm",
    "Sm",
    "Eu",
    "Gd",
    "Tb",
    "Dy",
    "Ho",
    "Er",
    "Tm",
    "Yb",
    "Lu",
    "Hf",
    "Ta",
    "W",
    "Re",
    "Os",
    "Ir",
    "Pt",
    "Au",
    "Hg",
    "Tl",
    "Pb",
    "Bi",
    "Po",
    "At",
    "Rn",
    "Fr",
    "Ra",
    "Ac",
    "Th",
    "Pa",
    "U",
    "Np",
    "Pu",
    "Am",
    "Cm",
    "Bk",
    "Cf",
    "Es",
    "Fm",
    "Md",
    "No",
    "Lr",
    "Rf",
    "Db",
    "Sg",
    "Bh",
    "Hs",
    "Mt",
    "Ds",
    "Rg",
    "Cn",
    "Nh",
    "Fl",
    "Mc",
    "Lv",
    "Ts",
    "Og",
}


def is_compound (text: str) :
  """
  Return True if text is a compound with a simple formula,
  consisting of a string of  element[count]  pairs,
  where [count] is an optional single- or two-digit number.
  e.g., H2SO4, NaCl, Li4Ti5O12
  Limitations: It will accept non-physical compounds, like KNOW
  """
  pos = 0
  end = len(text)
  while pos < end :
    if pos + 2 <= end and text[pos:pos+2] in elements :
      pos += 2
    elif text[pos:pos+1] in elements :
      pos += 1
    elif (pos > 0 and text[pos].isdigit ()
          and (not text[pos-1].isdigit ()
               or (pos > 1 and not text[pos-2].isdigit()))) :
      pos += 1
    else :
      break;

  return (pos == end)

for line in sys.stdin :
  #if len(line) >= 5 and line[1:3] in elements and line[3:5] in elements :
  if is_compound (line.strip()) :
    print ("&"+line, end="")
  elif len (line) > 1 and is_compound (line.split()[0]) :
    print ("&"+line, end="")
  else :
    print (line, end="")
