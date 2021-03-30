import quantities


PRONOUNS1 = {
        'en': {
                'i', 'we', 'me', 'us', 'myself', 'ourselves', 'mine', 'ours',
        },
        'de': {
                'ich', 'meiner', 'mir', 'mich', 'wir', 'unser', 'uns', 'mein',
                'meines', 'meinem', 'meinen', 'meine', 'meins', 'unserer',
                'unseres', 'unserem', 'unseren', 'unsere', 'unsers',
        },
        'it': {
                'io', 'me', 'mi', 'mia', 'mio', 'miei', 'mie', 'noi', 'ci',
                 'nostro', 'nostra', 'nostri', 'nostre',
        },
        'nl': {
                'ik', 'mij', 'me', 'mijne', 'wij', 'we', 'ons', 'onze',
        },
}
PRONOUNS2 = {
        'en': {
                'you', 'yourself', 'yours'
        },
        'de': {
                'du', 'deiner', 'dir', 'dich', 'ihr', 'euer', 'euch', 'dein',
                'deines', 'deinem', 'deinen', 'deine', 'deins', 'eurer',
                'eures', 'eurem', 'euren', 'eure',
        },
        'it': {
                'tu', 'te', 'ti', 'tuo', 'tua', 'tuoi', 'tue', 'voi', 'vi',
                'vostro', 'vostra', 'vostri', 'vostre'
        },
        'nl': {
                'jij', 'je', 'jou', 'jouwe', 'u', 'uwe', 'jullie'
        },
}


def guess_symbol(word, lang):
    word = word.lower()
    if word in PRONOUNS1[lang]:
        return 'speaker'
    if word in PRONOUNS2[lang]:
        return 'hearer'
    return quantities.guess_quantity(word)
