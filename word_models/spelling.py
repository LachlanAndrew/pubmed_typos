#!/usr/bin/python3
#!/home/llandrew/anaconda3/bin/python

import sys
import difflib as dl
import unidecode

import pdb

sys.path.insert(0, "../../pyspellchecker")
sys.path.insert(0, "../")
from spellchecker import SpellChecker
import autodict

from known_errs import known_errs, deliberate_misspellings, equivalents
import italian_vocab
import chinese
import guess_lang

if len (sys.argv) > 2 :
  model_prefix = sys.argv[1]
  sys.argv = sys.argv[1:]
else :
  model_prefix = None

fast = False

spell = SpellChecker(distance=1)
#spell = SpellChecker()

def char_range(c1, c2):
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in range(ord(c1), ord(c2)+1):
        yield chr(c)

capitals = set()
for i in char_range('A', 'Z') :
  capitals.add(i)

alphabet = {"'", "-"}
for i in char_range('a', 'z') :
  alphabet.add(i)
#alphabet.update (capitals)

endings = {"s":  ("ment", "oir", "ion", "ist", "ism", "ate", "er", "ure",
                  "ance", "ence", "hood", "iece", "ship", "ise", "ize",
                  "age", "gue", "gen", "ite", "oid", "gram", "graph",
                  "ic", "head", "board", "line", "house", "book", "room",
                  "ead", "ette", "tor", "oma", "tom", "dom", "ant", "ian",
                  "ing", "al", "ive", "able",        # not sure about these.
                 ),
           "es": ("ss", "ash", "box"),
           "ly": ("l", "le", "ive", "ing", "ent", "ant", "ous", "ed", "ate",
                  "ile", "ish", "less", "ful", "some", "id", "lar"),
           "r":  ("ide",),
           "ed": ("ion",),
           "d":  ("ate", "ize", "ise", "ace", "ice"),
           "al": ("ion", "ic", "ment"),
           "ic": ("gen", "nym"),
           "cy": ("ain",),
           "t":  ("ies",),
           "ness": ("ous", "ed"),
           "ism": ("ion",),
           "ist": ("ion",),
          }

swap_endings = {
  "ist"   : ("ic", "ism"),
  "ism"   : ("ic", "ist"),
  "ily"   : ("y",),
  "iness" : ("y",),
  "ably"  : ("able",),
  "ate"   : ("ative",),
}

# common errors, often causing incorrect "corrections"
wrong_endings = {
  "nts" : ("nce",),
  "ly"  : ("lly", "ally"),
  "ll"  : ("l",),
  "d"   : ("ed",),
  "ys"   : ("ies",),
}

middles = {
  "is"   : ("iz",),
  "iz"   : ("is",),
}

wrong_middles = {
  "q"  : ("cq",),
  "cq" : ("q",),
  "ge"  : ("dge",),
  "gi"  : ("dgi",),
  "dge"  : ("ge",),
  "dgi"  : ("gi",),
  "eing" : ("ing",),
  "ie"   : ("ei",),
  "ei"   : ("ie",),
  "sce"  : ("se"),
  "se"   : ("sce"),
  "able" : ("ible",),
  "ible" : ("able",),
  "ably" : ("ibly",),
  "ibly" : ("ably",),
  "ence" : ("ance",),
  "ance" : ("ence",),
  "enci" : ("anci",),
  "anci" : ("enci",),
  "ent" : ("ant",),
  "ant" : ("ent",),
  "ement": ("ment",),
  "ment": ("ement",),
  "eabl": ("abl",),
  "abl": ("eabl",),
}

name_suffixes = {
  "name": {
    "arabic": {
      "adeh",
      "allah",
      "allahi",
      "aziz",
      "elah",
      "llah",
      "oor",
      "uddin",
      "ullah",
      "ullahi",
      "ullahu",
      "zadeh",
      "zbek",
    },
    "slavic" : {
      "a",
      "ak",
      "arski",
      "cewicz",
      "cik",
      "chikov",
      "czak",
      "czyk",
      "da",
      "ecki",
      "ek",
      "enko",
      "enky",
      "er",
      "erski"
      "ersky"
      "estra",
      "etske",
      "etsky",
      "ev",
      "eva",
      "evich",
      "evsky",
      "ewich",
      "ewicz",
      "ewitz",
      "i",
      "ich",
      "ievich",
      "iewicz",
      "ik",
      "icow",
      "in",
      "ishky",
      "itsky",
      "ka",
      "kin",
      "ko",
      "kova",
      "kowski",
      "ky",
      "na",
      "nicki",
      "nikoff",
      "nikov",
      "nowicz",
      "o",
      "off",
      "ofsky",
      "or",
      "os",
      "ov",
      "ova",
      "ove",
      "ovic",
      "ovich",
      "ovics",
      "ovicz",
      "ovitch",
      "ovitz",
      "ovka",
      "ovna",
      "ovska",
      "ovski",
      "ovsky",
      "ow",
      "owicz",
      "owitz",
      "owka",
      "owski",
      "owsky",
      "sha",
      "ska",
      "ski",
      "sky",
      "tsov",
      "ycki",
      "y",
      "zak",
      "zinski",
      "zky",
      "zyk",
    },
    "greek" : {
      "akis",
      "akos",
      "e",
      "i",
      "is",
      "iou",
      "opolous",
      "opoulos",
      "opoulou",
      "opoulous",
      "opoulus",
      "opulo",
      "opulos",
      "opulous",
      "os",
      "ou",
      "oupoli",
      "oupolis",
    },
    "english": { "bert", "forth", "lyn", "lynn", "lynne",
                 "man", "son", "wright", },
    "french": { "eau", "eault", "jolais", "jolie",
                "nault", "neault", "pierre", "venu", },
    "germanic": { "ardt", "berg", "berger", "bert", "brecht",
                  "hart", "hardt", "hofer",
                  "kamp", "man", "mann", "meier", "meyer",
                  "parger", "perger",
                  "sberger", "schauer", "schmidt", "sen",
                  "sperger", "sson", "stahler", },
    "italian": { "ella", "elle", "elli", "ello",
                 "etta", "ette", "etti", "etto",
                 "i",
                 "onzzi", "ora", "ore", "ori", "otti", "otto", "ottola", "ozzi",
                 "ni","no", "tta", "ucci",
               },
    "yiddish": { "bach", "baum", "berg", "berger", "blatt", "bloom", "blum",
                 "buehler", "burg", "burger",
                 "feld", "garten", "haus", "heim", "hoefer", "hofer",
                 "kranz", "man", "mann",
                 "schein", "schild", "shein", "shtein", "shteyn",
                 "sohn", "stein", "steiner",
                 "thal", "vogel", "wasser", "zveig", "zweig", },
    }, 
  "place": {
  "arabic": {"abad", "astan", "istan", "stan"},
  "english": {"beach", "boro", "borough",
              "bridge", "bridges", "brook", "brough", "burn", "burne", "bury",
              "castle", "chester", "cliff", "cliffe", "crest", "croft", "creek",
              "dale", "don", "field", "fields", "ford",
              "gate", "green", "grove",
              "ham", "hampton", "haven", "hill", "holme", "hurst",
              "ingham", "ington",
              "lake", "land", "lea" "lee", "leigh",
              "market", "mead", "meadow", "mont", "moor", "mount", "mouth",
              "pool", "port",
              "ridge", "rock", "shire", "side", "stream",
              "sford", "sgate", "ston", "sville", 
              "thorpe", "ton", "tons", "town",
              "water", "wick", "wold", "wood", "worth",
              "vale", "view", "ville", "yard"},
  "french": { "bois", "castel", "champ", "champms", "chastel",
              "jeu", "laurier", "lieau", "lieu",
              "marchais", "prez", "regarde", "rivage",
              "soleil", "vais", "voir", "vois"},
  "germanic" : {"berg", "burg", "dorf", "dorff", "feldt", "feld",
                "hof", "holtz", "holz",
                "lund", "see", "stad", "stadt", "stedt", "strom", "torff",
                "wald", },
  }
}

# Words accidentally flagged as names
non_names = {
  "Aberdeen",
  "About",
  "Absent",
  "Africa",
  "African",
  "Africanism",
  "Africans",
  "Agar",
  "Albinism",
  "Albion",
  "Alike",
  "Alkali",
  "Allopathy",
  "Allot",
  "Alloy",
  "Alter",
  "Amber",
  "Ambers",
  "America",
  "American",
  "Americana",
  "Americanism",
  "Americans",
  "Americas",
  "Amid",
  "Amine",
  "Angel",
  "Anger",
  "Anglomania",
  "Anise",
  "Antigen",
  "Aqua",
  "Aquaria",
  "Arab",
  "Arabia",
  "Arabian",
  "Arable",
  "Arabs",
  "Aria",
  "Arian",
  "Arianism",
  "Arians",
  "Aryan",
  "Aryans",
  "Asia",
  "Asian",
  "Asians",
  "Attain",
  "Austral",
  "Australia",
  "Australian",
  "Australians",
  "Austria",
  "Austrian",
  "Auto",
  "Autos",
  "Back",
  "Backer",
  "Baker",
  "Bakers",
  "Bakery",
  "Bald",
  "Balder",
  "Baldy",
  "Balling",
  "Banana",
  "Bananas",
  "Band",
  "Banding",
  "Bandit",
  "Bandy",
  "Banging",
  "Bank",
  "Banker",
  "Banks",
  "Banner",
  "Bans",
  "Barge",
  "Bargy",
  "Baring",
  "Bark",
  "Barker",
  "Barn",
  "Barns",
  "Baron",
  "Barony",
  "Barter",
  "Bats",
  "Beat",
  "Beaten",
  "Beater",
  "Beatlemania",
  "Beatles",
  "Beats",
  "Beau",
  "Beaus",
  "Beaut",
  "Belay",
  "Belgian",
  "Bell",
  "Belling",
  "Bellow",
  "Belly",
  "Belt",
  "Bench",
  "Bencher",
  "Bend",
  "Bender",
  "Bendy",
  "Bent",
  "Berlin",
  "Bevel",
  "Biller",
  "Billow",
  "Billy",
  "Bind",
  "Binder",
  "Bindle",
  "Binds",
  "Biotech",
  "Bits",
  "Blazer",
  "Blazers",
  "Blazon",
  "Bock",
  "Boll",
  "Bolls",
  "Bone",
  "Boned",
  "Boner",
  "Bones",
  "Bonier",
  "Bonk",
  "Borage",
  "Border",
  "Bottle",
  "Bottled",
  "Bottler",
  "Bottles",
  "Bowled",
  "Bowleg",
  "Bowler",
  "Brat",
  "Brave",
  "Bravos",
  "Bridge",
  "Bridged",
  "Bridgend",
  "Bridger",
  "Bridges",
  "Brow",
  "Brown",
  "Browns",
  "Brows",
  "Bubble",
  "Bubbles",
  "Bulk",
  "Bulker",
  "Bulky",
  "Burial",
  "Burka",
  "Burkina",
  "Bust",
  "Buster",
  "Bustle",
  "Busts",
  "Busty",
  "Calais",
  "Calvinism",
  "Cameroon",
  "Canaan",
  "Canada",
  "Canadian",
  "Canadianism",
  "Canadians",
  "Canal",
  "Candle",
  "Candy",
  "Caracas",
  "Caring",
  "Carnage",
  "Carnal",
  "Carve",
  "Carven",
  "Carver",
  "Casaba",
  "Castor",
  "Cell",
  "Cellar",
  "Cells",
  "Chain",
  "Chains",
  "Chair",
  "Chakra",
  "Chakras",
  "Chard",
  "Charge",
  "Charm",
  "Chart",
  "Charter",
  "Charts",
  "Chatter",
  "Chatty",
  "Check",
  "Checker",
  "Checkoff",
  "Cheek",
  "Cheeks",
  "Cheep",
  "Cheer",
  "Chem",
  "Chennai",
  "Chew",
  "Chick",
  "Chime",
  "Chimp",
  "Chin",
  "China",
  "Chinas",
  "Chink",
  "Chinks",
  "Chins",
  "Chip",
  "Chit",
  "Chitin",
  "Chits",
  "Chow",
  "Chows",
  "Christian",
  "Christians",
  "Churn",
  "Cinema",
  "Cinerama",
  "Clad",
  "Clade",
  "Clang",
  "Clank",
  "Clans",
  "Collage",
  "Collar",
  "Collate",
  "Collector",
  "Collectors",
  "Colon",
  "Colonel",
  "Colonels",
  "Colonic",
  "Colons",
  "Color",
  "Colour",
  "Condo",
  "Condom",
  "Condor",
  "Condos",
  "Congo",
  "Constant",
  "Corinth",
  "Cost",
  "Cots",
  "Court",
  "Crank",
  "Cranky",
  "Cyber",
  "Cyclonic",
  "Czech",
  "Dalian",
  "Dank",
  "Daring",
  "Darn",
  "Darner",
  "Dash",
  "Dasher",
  "Debate",
  "Debian",
  "Deep",
  "Deepen",
  "Deeper",
  "Deeps",
  "Desk",
  "Despot",
  "Devil",
  "Diamante",
  "Dies",
  "Digit",
  "Diva",
  "Divan",
  "Divas",
  "Dollar",
  "Domino",
  "Donor",
  "Doodle",
  "Dorky",
  "Dots",
  "Drab",
  "Drag",
  "Drake",
  "Drama",
  "Dramas",
  "Drug",
  "Dung",
  "Dungs",
  "Electrotechnical",
  "Equestrian",
  "Equestrianism",
  "Equestrians",
  "Eurasia",
  "Eurasian",
  "Eurasians",
  "Euro",
  "European",
  "Europeans",
  "Euros",
  "Ever",
  "Every",
  "Farm",
  "Fedora",
  "Fiery",
  "Flora",
  "Florin",
  "Flowed",
  "Flower",
  "Frack",
  "Fracker",
  "Frank",
  "From",
  "Furs",
  "Gander",
  "Gang",
  "Ganglia",
  "Gangs",
  "Garb",
  "Gassy",
  "Gawk",
  "Gawker",
  "Gawky",
  "Gazing",
  "Geotechnical",
  "German",
  "Germane",
  "Ghana",
  "Giant",
  "Gird",
  "Girder",
  "Girdle",
  "Girds",
  "Glen",
  "Gnat",
  "Gold",
  "Golder",
  "Gore",
  "Gored",
  "Grab",
  "Grader",
  "Grand",
  "Grander",
  "Grandma",
  "Grape",
  "Graph",
  "Grater",
  "Gray",
  "Grayer",
  "Grin",
  "Grits",
  "Guatemala",
  "Gulag",
  "Guru",
  "Gurus",
  "Gust",
  "Gusto",
  "Gusts",
  "Gusty",
  "Guyana",
  "Habit",
  "Halal",
  "Hams",
  "Handler",
  "Hanky",
  "Hare",
  "Harem",
  "Hares",
  "Hark",
  "Harsh",
  "Harsher",
  "Hedge",
  "Hedged",
  "Hedger",
  "Hedges",
  "Hellenic",
  "Hellenism",
  "Hint",
  "Hinter",
  "Hints",
  "Hosanna",
  "Hyderabad",
  "Imam",
  "Imams",
  "India",
  "Indian",
  "Indiana",
  "Indianan",
  "Indians",
  "Info",
  "Inter",
  "Intern",
  "Interns",
  "Inters",
  "Iran",
  "Irani",
  "Iranian",
  "Islam",
  "Islamabad",
  "Islams",
  "Jack",
  "Jangle",
  "Jerk",
  "Jerker",
  "Jerkin",
  "Jerky",
  "Jungian",
  "Jungle",
  "Jungles",
  "Junior",
  "Kaiser",
  "Kaisers",
  "Kale",
  "Kandahar",
  "Karate",
  "Kits",
  "Knit",
  "Kolas",
  "Korea",
  "Korean",
  "Koreans",
  "Krakow",
  "Kurd",
  "Lamp",
  "Land",
  "Lander",
  "Lark",
  "Last",
  "Leninism",
  "Lent",
  "Liar",
  "Liberty",
  "Linger",
  "Liquid",
  "List",
  "Listen",
  "Lister",
  "Lists",
  "Loch",
  "Lochs",
  "Logo",
  "Logon",
  "Logos",
  "Luck",
  "Lucky",
  "Macau",
  "Mach",
  "Macho",
  "Machos",
  "Madam",
  "Main",
  "Maine",
  "Mains",
  "Major",
  "Malady",
  "Malaria",
  "Malay",
  "Malaya",
  "Malayan",
  "Male",
  "Males",
  "Mali",
  "Malibu",
  "Mall",
  "Manish",
  "Manna",
  "Manor",
  "Mantis",
  "Mantle",
  "Manual",
  "March",
  "Marcher",
  "Marine",
  "Mariner",
  "Mark",
  "Marks",
  "Mash",
  "Masher",
  "Mask",
  "Masker",
  "Mast",
  "Master",
  "Mats",
  "Maxim",
  "Maxima",
  "Mayan",
  "Mayans",
  "Mazurka",
  "Median",
  "Mega",
  "Mentor",
  "Metal",
  "Metals",
  "Micro",
  "Micron",
  "Microns",
  "Milan",
  "Milk",
  "Milker",
  "Milky",
  "Mini",
  "Minim",
  "Minima",
  "Mining",
  "Minion",
  "Mink",
  "Mint",
  "Minty",
  "Mirage",
  "Misc",
  "Mist",
  "Mister",
  "Misty",
  "Mitre",
  "Mohair",
  "Mongol",
  "Mongolia",
  "Mongolian",
  "Mongols",
  "Monk",
  "Mont",
  "Montage",
  "Moon",
  "Moons",
  "Moscow",
  "Motion",
  "Motor",
  "Much",
  "Muddle",
  "Muddy",
  "Mule",
  "Mules",
  "Mumbai",
  "Mural",
  "Murder",
  "Murky",
  "Muse",
  "Mused",
  "Muser",
  "Muses",
  "Mush",
  "Musher",
  "Mushy",
  "Musing",
  "Musk",
  "Musky",
  "Muslim",
  "Muslims",
  "Muzak",
  "Naturopathy",
  "Naval",
  "Nave",
  "Navel",
  "Naves",
  "Nepal",
  "Nepali",
  "Nepalis",
  "Niche",
  "Nick",
  "Nicker",
  "Noon",
  "Noons",
  "Obey",
  "Osaka",
  "Pack",
  "Packer",
  "Pajamas",
  "Panama",
  "Panamanian",
  "Panky",
  "Pant",
  "Pants",
  "Pappy",
  "Parade",
  "Parapet",
  "Paring",
  "Parish",
  "Park",
  "Parker",
  "Parmesan",
  "Parole",
  "Passage",
  "Past",
  "Pasta",
  "Pastas",
  "Paste",
  "Paster",
  "Pasts",
  "Pasty",
  "Path",
  "Paths",
  "Pawl",
  "Peer",
  "Peerage",
  "Peers",
  "Peril",
  "Perish",
  "Perk",
  "Perky",
  "Persia",
  "Persian",
  "Persians",
  "Petri",
  "Piano",
  "Pianos",
  "Pick",
  "Picker",
  "Pickoff",
  "Picky",
  "Pied",
  "Pier",
  "Pink",
  "Pinker",
  "Pinky",
  "Plan",
  "Plane",
  "Plasma",
  "Platonic",
  "Platonism",
  "Platoon",
  "Plot",
  "Plush",
  "Pluto",
  "Poland",
  "Polar",
  "Polish",
  "Polite",
  "Polka",
  "Poll",
  "Poller",
  "Polymer",
  "Polytechnic",
  "Post",
  "Poster",
  "Potter",
  "Potters",
  "Pottery",
  "Pram",
  "Prem",
  "Presto",
  "Print",
  "Prize",
  "Prized",
  "Prizes",
  "Program",
  "Prom",
  "Proms",
  "Prove",
  "Punish",
  "Pushpin",
  "Putt",
  "Putter",
  "Putts",
  "Putty",
  "Pyromania",
  "Qatar",
  "Qatari",
  "Quail",
  "Quaint",
  "Quin",
  "Quiz",
  "Rabid",
  "Radar",
  "Radon",
  "Raft",
  "Raisin",
  "Rajah",
  "Rang",
  "Range",
  "Ranger",
  "Rangy",
  "Rank",
  "Ranker",
  "Rapt",
  "Rash",
  "Rasher",
  "Raster",
  "Rather",
  "Rave",
  "Raved",
  "Ravel",
  "Raven",
  "Ravens",
  "Raver",
  "Raves",
  "Raving",
  "Read",
  "Recycle",
  "Recycled",
  "Recycler",
  "Recycles",
  "Regular",
  "Rest",
  "Ride",
  "Rink",
  "Rite",
  "River",
  "Rivers",
  "Robin",
  "Rock",
  "Rocker",
  "Rocky",
  "Rolled",
  "Roller",
  "Roma",
  "Roman",
  "Romanic",
  "Root",
  "Rooter",
  "Rose",
  "Roses",
  "Roster",
  "Royal",
  "Ruck",
  "Rupee",
  "Rusk",
  "Saga",
  "Said",
  "Sail",
  "Sails",
  "Saint",
  "Saints",
  "Salad",
  "Salami",
  "Salamis",
  "Salk",
  "Salmon",
  "Samaria",
  "Samba",
  "Sambas",
  "Sampan",
  "Samsung",
  "Sand",
  "Sandal",
  "Sander",
  "Sandy",
  "Sangria",
  "Sank",
  "Santa",
  "Sashay",
  "Satan",
  "Satanic",
  "Satanism",
  "Satay",
  "Satin",
  "Satins",
  "Saudi",
  "Saudis",
  "Savage",
  "Savant",
  "Scar",
  "Scare",
  "Scarp",
  "Scars",
  "Scary",
  "Schema",
  "Scheme",
  "Second",
  "Sedan",
  "Sedans",
  "Sedate",
  "Selvage",
  "Semen",
  "Senate",
  "Senile",
  "Sent",
  "Serge",
  "Serif",
  "Shade",
  "Shady",
  "Shah",
  "Shahs",
  "Shaker",
  "Shaky",
  "Shale",
  "Shall",
  "Shalt",
  "Sham",
  "Shaman",
  "Shamans",
  "Shame",
  "Shams",
  "Shave",
  "Shaven",
  "Shaver",
  "Shaving",
  "Sheik",
  "Sheikh",
  "Sheikhs",
  "Sheiks",
  "Shell",
  "Shin",
  "Shine",
  "Shined",
  "Shiner",
  "Shines",
  "Shining",
  "Ship",
  "Shiver",
  "Shoe",
  "Shoes",
  "Shrill",
  "Sienna",
  "Silk",
  "Silky",
  "Sing",
  "Singe",
  "Singer",
  "Single",
  "Sings",
  "Sink",
  "Sinker",
  "Sitar",
  "Siting",
  "Skit",
  "Skol",
  "Slag",
  "Slaughter",
  "Slaw",
  "Sled",
  "Slim",
  "Slimy",
  "Smiler",
  "Solid",
  "Solo",
  "Solos",
  "Somali",
  "Somalia",
  "Some",
  "Sonar",
  "Sonars",
  "Sonata",
  "Sound",
  "Sounder",
  "Sounds",
  "Sour",
  "Span",
  "Spat",
  "Spiky",
  "Spire",
  "Split",
  "Splits",
  "Staff",
  "Stank",
  "Star",
  "Stare",
  "Starer",
  "Stark",
  "Starker",
  "Stars",
  "Start",
  "Stash",
  "Stem",
  "Step",
  "Stoker",
  "Stop",
  "Strain",
  "Strand",
  "Strange",
  "Strap",
  "Strata",
  "Stray",
  "Stud",
  "Study",
  "Such",
  "Sugar",
  "Sulk",
  "Sulky",
  "Sultan",
  "Sultana",
  "Sultans",
  "Sundae",
  "Sunday",
  "Super",
  "Supra",
  "Sushi",
  "Swam",
  "Swamp",
  "Tale",
  "Talent",
  "Tales",
  "Taliban",
  "Tamale",
  "Tamp",
  "Tang",
  "Tangy",
  "Tank",
  "Telepathy",
  "Tell",
  "Teller",
  "Tells",
  "Telly",
  "Temp",
  "Temper",
  "Templar",
  "Temple",
  "Temps",
  "Tempt",
  "Than",
  "Thane",
  "Thank",
  "Thanks",
  "Theater",
  "Theaters",
  "Thee",
  "Them",
  "Theme",
  "Then",
  "Tiger",
  "Tigers",
  "Timor",
  "Titan",
  "Titanic",
  "Titans",
  "Titian",
  "Token",
  "Tokenism",
  "Tokens",
  "Tomato",
  "Tong",
  "Tonga",
  "Tongan",
  "Tongans",
  "Tongs",
  "Toque",
  "Track",
  "Tracker",
  "Tracks",
  "Trans",
  "Trash",
  "Trend",
  "Trendy",
  "Trick",
  "Tricker",
  "Tricky",
  "Trojan",
  "Tron",
  "Trots",
  "Tsar",
  "Tulip",
  "Tulips",
  "Tuna",
  "Tunas",
  "Turk",
  "Turks",
  "Turn",
  "Turner",
  "Tusk",
  "Urban",
  "Urbanism",
  "Utopia",
  "Utopian",
  "Utopianism",
  "Utopians",
  "Utopias",
  "Valid",
  "Vandal",
  "Veer",
  "Veers",
  "Vellum",
  "Venue",
  "Venus",
  "Verb",
  "Verge",
  "Victorian",
  "Victorianism",
  "Victorians",
  "Villa",
  "Village",
  "Villain",
  "Villas",
  "Vitae",
  "Vital",
  "Wacky",
  "Waking",
  "Wales",
  "Walk",
  "Walker",
  "Ward",
  "Warder",
  "Wart",
  "Watch",
  "Watcher",
  "Water",
  "Waters",
  "Watery",
  "Webs",
  "Wend",
  "West",
  "Western",
  "Westernism",
  "Westerns",
  "Whisk",
  "Whist",
  "Wick",
  "Wicker",
  "Wicks",
  "Wink",
  "Winker",
  "Wins",
  "Witty",
  "Wolf",
  "Wrestle",
  "Wrestled",
  "Wrestler",
  "Wrestles",
  "Xenon",
  "Yakut",
  "Yank",
  "Yell",
  "Yellow",
  "Yells",
  "Yoga",
  "Your",
  "Zion",
  "Zombie",
  "Zombies",
}

def highlight_change (candidate, word) :
  seq_matcher = dl.SequenceMatcher (None, word, candidate)
  retval = []
  for type, w1, w2, c1, c2 in seq_matcher.get_opcodes() :
    if type == "equal" :
      retval.append (word[w1: w2])
    elif type == "insert" :
      retval.extend (["(", candidate[c1:c2], ")"])
    elif type == "delete" :
      retval.extend (["-", word[w1:w2], "-"])
    elif type == "replace" :
      retval.extend (["[", word[w1:w2], "/", candidate[c1:c2], "]"])

  return "".join (retval)

if not fast :
  for extra_file in ("extra_words.txt", "extra-nondictionary-words.txt",
                     "words_foreign.txt", "words_trademarks.txt",
                     "words_medical.txt") :
    print (f"Loading {extra_file}...", file=sys.stderr)
    try :
      with open (extra_file, "r") as f :
        extra = f.readlines();
      #extra = [e.rstrip() for e in extra if not e.startswith('#')]
      extra = [e[0:(e.find('#') % (len(e)+1))].rstrip() for e in extra]
      spell.word_frequency.load_words(extra)
    except FileNotFoundError :
      print (f"Skipping {extra_file}", file=sys.stderr)
  extra = ""    # clear memory

  try :
    from words_space_separated import space_separated, dash_separated
    for extra in (space_separated, dash_separated) :
      spell.word_frequency.load_words([w for w in extra])
  except ModuleNotFoundError :
    print ("Could not find module words_space_separated. Skipping", file=sys.stderr)

# Process command line arguments
if len (sys.argv) > 1 and sys.argv[1] == "--learn" :
  learning = True
  del sys.argv[1]
else :
  learning = False

if len (sys.argv) > 1 :
  if sys.argv[1] == '-' :
    in_file = ""
  else :
    in_file = sys.argv[1]
  del sys.argv[1]
else :
  in_file = "single_words_tmp"

languages = ["en", "ar", "cy", "da", "de", "es", "fr",
           "hi", "in", "it", "jp", "kr", "ma", "nl", "pl",
           "sm", "slv", "tl", "zh",
           "vn",
           "med", "chem"]

if len (sys.argv) > 1 and sys.argv[1] == "--" :
    languages = sys.argv[2:]

  # "zh" and "it" are separate
  # If these are changed, also update loading of foreign words, below
print ("Initializing models...", file=sys.stderr)
models = guess_lang.init([l for l in languages if l not in ("zh", "it")], prefix = model_prefix)

foreign = {}
foreign_counts = {"total": 0}
if not fast :
  print ("Loading foreign words...", file=sys.stderr)
  lang_map = {"tl": "tagalog", "id": "indonesian", "in": "hindi",
              "hi": "hawaiian", "ma": "maori"}
  #for lang in ("fr", "de", "es", "nl", "cy", "da", # "it",
  #             "ar", "jp", "kr", "pl", "sm", "vn", "zh",
  #             "tagalog", "indonesian", "hindi", "hawaiian", "maori") :
  for lang in (l for l in languages if l != "en") :
    if lang in lang_map :
      lang = lang_map[lang]
    print (lang, end="...", file=sys.stderr, flush=True)

    with open ("words_"+lang+".txt") as f :
      extras = {e.rstrip() for e in f.readlines() if not e.startswith('#')}

    extra_no_accent = {unidecode.unidecode(e.lower()) for e in extras}

    foreign[lang] = extras.union(extra_no_accent)
    foreign_counts[lang] = 0

  # Special case with compression, as vocab is > 10 times larger than others
  if "it" in languages :
    lang = "it"
    print (lang, end="...", file=sys.stderr, flush=True)
    italian_vocab.read_vocab("words_it_cache.txt", "words_it.txt")
    foreign_counts[lang] = 0
    print (file=sys.stderr)

  if "zh" in languages :
    foreign_counts["zh"] = 0


print ("Processing words from", in_file, "...", file=sys.stderr)
all_words = []
with open (in_file, "r") if in_file else sys.stdin as f :
  for word in f :
    word = word.rstrip()
    if (not word or '#' in word or "&" in word
                 or any([((w<'a' or w>'z') and (w<'A' or w>'Z'))
                         and not w in "_'" for w in word])):
      continue

    low = word.lower ()

    if False :
      import hyphenation
      if low in hyphenation.firsts or low in hyphenation.seconds :
        continue

    all_words.append (word)
    if len (all_words) % 1024 == 0 :
      print (len(all_words), "processed\r", file=sys.stdout)

word_idx = {idx:word for word, idx in enumerate (all_words)}

print (len (all_words), "words              ")

## Names
name_suffix_exclusions = {
  "arabic": { "atipov", "lahpur", "ov" },
  "indian": { "abad", "money", "nism" }
}

for lang in ("arabic", "indian") :
  for pref in {"arabic": ("Abdul", "Abdel", "Abdi"),
               "indian": ("Anantha", "Bhatt", "Bhav", "Brahma",
                         "Chanda", "Chandra", "Chidam",
                         "Dhana", "Dharam", "Dharma",
                         "Gaja", "Ganga", "Giri", "Gopal", "Govind",
                         "Indra",
                         "Jagan", "Jha", "Jahan", "Jaya", "Jeya",
                         "Krishna", "Kumar", "Lakshmi", "Madhu", "Narayan",
                         "Shiva", "Sidda", "Siva", "Sree", "Subra", "Surya"),
              }[lang] :
    if pref in word_idx :
      if lang not in name_suffixes["name"] :
        name_suffixes["name"][lang] = set()
      base = word_idx[pref]
      while all_words[base].startswith(pref) :
        new_word = all_words[base][len(pref):]
        if not new_word in name_suffix_exclusions[lang] :
          name_suffixes["name"][lang].add(new_word)
        base += 1

all_name_suffixes = {}
for n in ("name", "place") :
  all_name_suffixes[n] = {name:lang for lang in name_suffixes[n]
                                    for name in name_suffixes[n][lang]
                                          if len (name) > 3 or name == "son"}
name_suff_by_len = {"name": {}, "place": {}}
for n in ("name", "place") :
  for suff in all_name_suffixes[n] :
    sl = len (suff)
    if not sl in name_suff_by_len[n] :
      name_suff_by_len[n][sl] = {}
    name_suff_by_len[n][sl][suff] = all_name_suffixes[n][suff]

## Main loop
names = set()
words = autodict.AutoDict()
for word in all_words:

    low = word.lower ()
    #if word in ("Abbeydale", "Abbeygate"): pdb.set_trace ()

    if low in known_errs :
      if not learning :
        words[word]["&"] = known_errs[low]
        print (known_errs[low], word, "&")
      continue

    if low in deliberate_misspellings :
      if not learning :
        words[word]["="] = deliberate_misspellings[low]
        print (deliberate_misspellings[low], word, "=")
      continue

    if low in equivalents :
      if not learning :
        words[word]["="] = equivalents[low]
        print (equivalents[low], word, "=")
      continue

    if (spell.known ([word])) :
      if not learning :
        words[word]["yes"] = word
        print (word, "   ", word)
      continue

    guessed_lang = ','.join(guess_lang.guess_lang (word, models, topn=2)[0])
    words[word]["guess"][guessed_lang] = word

    done = False
    for n in ("name", "place") :
      for ln in name_suff_by_len[n] :
        if ln <= len(word) - 2 and word[-ln:] in name_suff_by_len[n][ln] :
          lang = name_suff_by_len[n][ln][word[-ln:]]
          if lang != "english" and ln > len(word) - 3 :
            continue
          base_word = word[0:-ln]
          flag = f"base: {base_word} {n} {lang}"
          if flag in names :
            continue
          names.add(flag)
          if base_word in word_idx :
            base = word_idx[base_word]
            names.add(base_word)
            print ("base:" + base_word, "trigger", word, "lang", lang, n)
            while all_words[base].startswith(base_word) :
              loop_word = all_words[base]
              if loop_word[len(base_word):] in name_suffixes[n][lang] :
                names.add (loop_word)
                words[loop_word][n][lang] = loop_word
                print (" ", n, loop_word)
              else :
                print ("-", n, loop_word)
              base += 1
            done = True
            break
          else :        # only long suffixes. TODO: Reduce duplicate code
                        # Should only do this if no non-missing suffix is found
            base = word_idx[word]
            print ("base:" + base_word, "(missing) trigger",
                   word, "lang", lang, n)
            while all_words[base].startswith(base_word) :
              for len_loop in name_suff_by_len[n] :
                loop_word = all_words[base]
                if loop_word[len(base_word):] in name_suff_by_len[n][len_loop] :
                  names.add (loop_word)
                  words[loop_word][n][lang] = loop_word
                  print (" ", n, loop_word)
                  break
              base += 1
            done = True
            break

    if done :
      pass
    #if word in names :
    #  continue

    done = False
    for end in wrong_middles :
      if word.find(end) >= 0 :
        done = False
        for alt_end in wrong_middles[end] :
          alt = word.replace (end, alt_end)
          if spell.known ([alt]) :
            if not learning :
              words[word]["*.*"][f"{end}/{alt_end}"]= alt
              print (alt, word, "*.*", end, alt_end)
            done = True
            break
        if done :
          break
    #if done :
    #  continue

    done = False
    for suffix in swap_endings :
      if word.endswith (suffix) :
        w = word[0:-len(suffix)]
        for end in swap_endings[suffix] :
          if spell.known ([w + end]) :
            if not learning :
              words[word]["###"][f"{suffix}/{end}"] = word.replace(suffix, end)
              print (word, " ", word, "###", suffix, end)
            done = True
            break
      if done :
        break
    #if done :
    #  continue

    done = False
    for end in middles :
      if word.find(end) >= 0 :
        done = False
        for alt_end in middles[end] :
          alt = word.replace (end, alt_end)
          if spell.known ([alt]) :
            if not learning :
              words[word]["#.#"][f"{end}/{alt_end}"] = alt
              print (word, word, "#.#", end, alt_end)
            done = True
            break
        if done :
          break
    #if done :
    #  continue

    done = False
    for suffix in wrong_endings :
      if word.endswith (suffix) :
        w = word[0:-len(suffix)]
        for end in wrong_endings[suffix] :
          if spell.known ([w + end]) :
            if not learning :
              words[word]["**"][f"{suffix}/{end}"] = w+end
              print (w + end, word, "**", suffix, end)
            done = True
            break
      if done :
        break
    #if done :
    #  continue

    #candidate = spell.correction(word).replace(" ", "_")
    candidate, score, freq, sim, reason = spell.ranked_candidates(word, keep_scores=True)[0]
    candidate = candidate.replace(" ", "_")

    # Some words in the default dictionary are wrong
    if candidate in known_errs :
      candidate = word

    if candidate.lower() != low and low.startswith(candidate.lower()) :
      suffix = word[len(candidate):]
      done = False
      if suffix in endings :
        for end in endings[suffix] :
          if candidate.endswith (end) :
            if not learning :
              words[word]["#"] = word[0:len(candidate)] + "+" +suffix
              print (words[word]["#"], " ", word, "#")
            done = True
            break
        #if done :
        #  continue

    # If the changes are common errors (currently [un]doubling a letter)
    # assume it is a spelling error
    # (rather than foreign, so do this before foreign check)
    seq_matcher = dl.SequenceMatcher (None, low, candidate.lower())
    seq_matcher = [s for s in seq_matcher.get_opcodes() if s[0] != "equal"]
    error = True
    for tag, w1, w2, c1, c2 in seq_matcher :
      if tag == "replace" :
        error = False
        break
      if tag == "insert" :
        if not (c2 == c1+1 and candidate[c1]
                                in low[max(0, w2-1) : min(w1+1, len (low))]) :
          error = False
          break
      else :
        if not (w2 == w1+1 and low[w1]
                               in candidate[max(0, c2-1)
                                            : min(c1+1, len(candidate))]) :
          error = False
          break
    if error and seq_matcher :
      if not learning :
        words[word][":"] = candidate
        print (candidate, word, ":")
      #continue

    any_foreign = False
    for lang in foreign :
      if word in foreign[lang] or low in foreign[lang] :
        foreign_counts[lang] += 1
        any_foreign = True
        if not learning :
          words[word]["##"][lang] = word
          print (word, word, "##", lang)
    if "it" in languages and (italian_vocab.known(word)
                           or italian_vocab.known(low)) :
      lang = "it"
      foreign_counts[lang] += 1
      any_foreign = True
      if not learning :
        words[word]["##"][lang] = word
        print (word, word, "##", lang)
    if "zh" in languages and (chinese.known(word) or chinese.known(low)) :
      lang = "zh"
      foreign_counts[lang] += 1
      any_foreign = True
      if not learning :
        words[word]["##"][lang] = word
        print (word, word, "##", lang)
    if any_foreign :
      foreign_counts["total"] += 1
      #continue

      if learning and not done :
        words[word]["learn"] = candidate
        print (suffix, candidate, flush=True)
        #continue

    # Flag a known suffix, following an unselected ending
    if candidate != word :
      if word.startswith(candidate) :
        suffix = word[len(candidate):]
        done = False
        if suffix in endings :
          if learning :
            words[word]["learn"] = (candidate, highlight_change(candidate, word), ">")
            print (candidate, highlight_change(candidate, word), word, ">")
          else :
            words[word][">"] = (candidate, suffix)
            print (suffix, candidate, " ", word, ">", suffix)
          #ontinue
        else :
          if learning :
            words[word]["learn"] = (candidate, highlight_change(candidate, word), ">>")
            print (candidate, highlight_change(candidate, word), word, ">>")
          else :
            words[word][">>"] = (candidate, suffix)
            print (suffix, candidate, " ", word, ">>")
          #continue

      if word.endswith(candidate) :
        if learning :
          words[word]["learn"] = (candidate, highlight_change(candidate, word), "<<")
          print (candidate, highlight_change(candidate, word), word, "<")
        else :
          words[word]["<"] = (candidate, word[0:-len(candidate)])
          print (word[0:-len(candidate)], candidate, word, "<")
        #continue

    if not learning :
      words[word]["?"] = candidate if candidate != word else None
      print (candidate, word, flush=True)
      #continue

    if learning :
      words[word]["learn"] = (candidate, highlight_change(candidate, word),
                              "$" if candidate == word else "+")
      print (candidate, highlight_change(candidate, word), word,
             "$" if candidate == word else "+", flush=True)

print ("\nNames\n")
for n in sorted(names) :
  print (n)

print ("\nWords\n")
for w in words :
  print (str({w:words[w]})[1:-1].replace("'__type__': 'AutoDict', ", ""))

print ()
for lang in foreign_counts :
  print (lang, foreign_counts [lang])


# ready for deletion
def old_routine () :
  import nltk
  from nltk.metrics.distance import jaccard_distance
  from nltk.metrics.distance import edit_distance
  from nltk.util import ngrams
  from nltk.corpus import words

  try :
    correct_words = words.words()
  except :
    nltk.download('words')
    correct_words = words.words()

  def char_range(c1, c2):
      """Generates the characters from `c1` to `c2`, inclusive."""
      for c in range(ord(c1), ord(c2)+1):
          yield chr(c)

  alphabet = {"'", "-"}
  for i in char_range('a', 'z') :
    alphabet.add(i)
  for i in char_range('A', 'Z') :
    alphabet.add(i)


  for word in sys.stdin :
      word = word.rstrip ()
      if not word :
        continue

      if {w for w in word}.difference(alphabet) :
        continue

      elif word in correct_words: 
        print (word, word)
        continue
      else :
        candidates = [(jaccard_distance(set(ngrams(word, 2)),
                                  set(ngrams(w, 2))),w)
                for w in correct_words if w[0]==word[0]]
        if not candidates :
          candidates = [(edit_distance(word, w),w) for w in correct_words
                                                   if w[0]==word[0]]
        if candidates :
          candidates = [a for a in sorted(candidates, key = lambda val:val[0])[0][1]]
        else :
          for i in range (1, len(word)-1) :
            pre = word[0:i]
            post = word[i:]

            if pre in correct_words and post in correct_words :
              candidates.append(pre + "_" + post)

          # Should sort by commonness of words

        if candidates :
          print (candidates, word)


