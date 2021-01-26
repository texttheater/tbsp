import numpy as np
import pathlib
import sys


sys.path.append(str(pathlib.Path(__file__).parent / 'ext' / 'ElMoForManyLangs'
        ))


from elmoformanylangs import Embedder


elmo_en = None
elmo_de = None
elmo_nl = None
elmo_it = None


def embed_sentence(sentence, lang='en'):
    global elmo_en, elmo_de, elmo_it, elmo_nl
    if lang == 'en':
        if not elmo_en:
            elmo_en = Embedder('models/ElMoForManyLangs/en')
        return elmo_en.sents2elmo((sentence,))[0]
    elif lang == 'de':
        if not elmo_de:
            elmo_de = Embedder('models/ElMoForManyLangs/de')
        return elmo_de.sents2elmo((sentence,))[0]
    elif lang == 'it':
        if not elmo_de:
            elmo_de = Embedder('models/ElMoForManyLangs/it')
        return elmo_de.sents2elmo((sentence,))[0]
    elif lang == 'nl':
        if not elmo_de:
            elmo_de = Embedder('models/ElMoForManyLangs/nl')
        return elmo_de.sents2elmo((sentence,))[0]
    else:
        raise ValueError(f'language not supported: {lang}')
