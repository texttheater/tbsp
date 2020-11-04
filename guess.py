import nltk
nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
LEMMATIZER = WordNetLemmatizer()


def guess_name(fragment, word):
    string = '"{}"'.format(word.lower().replace('"', "'"))
    return replace('"tom"', string, fragment)


def guess_concept_from_word(fragment, word):
    result = []
    for clause in fragment:
        if clause[2] == '"n.00"':
            lemma = LEMMATIZER.lemmatize(word, pos='n').lower()
            result.append((clause[0], lemma, '"n.01"', clause[3]))
        elif clause[2] == '"v.00"':
            lemma = LEMMATIZER.lemmatize(word, pos='v').lower()
            result.append((clause[0], lemma, '"v.01"', clause[3]))
        elif clause[2] == '"a.00"':
            lemma = LEMMATIZER.lemmatize(word, pos='a').lower()
            result.append((clause[0], lemma, '"a.01"', clause[3]))
        elif clause[2] == '"r.00"':
            lemma = LEMMATIZER.lemmatize(word, pos='r').lower()
            result.append((clause[0], lemma, '"r.01"', clause[3]))
        else:
            result.append(clause)
    return tuple(result)


def guess_concept_from_lemma(fragment, lemma):
    result = []
    for clause in fragment:
        if clause[2] == '"n.00"':
            result.append((clause[0], lemma, '"n.01"', clause[3]))
        elif clause[2] == '"v.00"':
            result.append((clause[0], lemma, '"v.01"', clause[3]))
        elif clause[2] == '"a.00"':
            result.append((clause[0], lemma, '"a.01"', clause[3]))
        elif clause[2] == '"r.00"':
            result.append((clause[0], lemma, '"r.01"', clause[3]))
        else:
            result.append(clause)
    return tuple(result)


def replace(old, new, obj):
    if old == obj:
        return new
    if isinstance(obj, tuple):
        return tuple(replace(old, new, e) for e in obj)
    return obj

