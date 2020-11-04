import collections
import random


class Vocabulary:

    def __init__(self, train_data, unk_prob=0.2):
        """Creates a vocabulary from training data.

        train_data is a sequence of occurrences of vocabulary items.

        Singletons while be replaced with __UNKNOWN__ with probability
        unk_prob.
        """
        counter = collections.Counter(train_data)
        self._w2i = {'__UNKNOWN__': 0}
        self._i2w = ['__UNKNOWN__']
        for word, freq in counter.items():
            if freq == 1 and random.random() < unk_prob:
                self._w2i['__UNKNOWN__'] += 1
            else:
                self._w2i[word] = len(self._w2i)
                self._i2w.append(word)

    def w2i(self, word):
        """Returns the int ID for the given word, or 0 if unknown.
        """
        return self._w2i.get(word, 0)

    def i2w(self, word_id):
        """Returns the word for the given ID."""
        return self._i2w[word_id]

    def __len__(self):
        return len(self._w2i)
