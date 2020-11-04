# FIXME support languages other than English


import re


def guess_times(fragment):
    result = []
    for clause in fragment:
        if clause[1] == 'ClockTime':
            result.append((clause[0], clause[1], clause[2], quote(guess_clock_time(unquote(clause[3])))))
        elif clause[1] == 'DayOfMonth':
            result.append((clause[0], clause[1], clause[2], quote(guess_day_of_month(unquote(clause[3])))))
        elif clause[1] == 'DayOfWeek':
            result.append((clause[0], clause[1], clause[2], quote(guess_day_of_week(unquote(clause[3])))))
        elif clause[1] == 'Decade':
            result.append((clause[0], clause[1], clause[2], quote(guess_year_of_century(unquote(clause[3])))))
        elif clause[1] == 'MonthOfYear':
            result.append((clause[0], clause[1], clause[2], quote(guess_month_of_year(unquote(clause[3])))))
        elif clause[1] == 'YearOfCentury':
            result.append((clause[0], clause[1], clause[2], quote(guess_year_of_century(unquote(clause[3])))))
        else:
            result.append(clause)
    return tuple(result)


### CLOCK TIMES ###############################################################


AM_PATTERN = re.compile(r'(?P<rest>.+?)~?[Aa]\.?[Mm]\.?$')
PM_PATTERN = re.compile(r'(?P<rest>.+?)~?[Pp]\.?[Mm]\.?$')
QUARTER_TO_PATTERN = re.compile(r'(?:a~)?quarter~(?:to|till)~(?P<rest>.+)$')
QUARTER_PAST_PATTERN = re.compile(r'(?:a~)?quarter~(?:past|after)~(?P<rest>.+)$')
HALF_PAST_PATTERN = re.compile(r'(?:a~)?half~past~(?P<rest>.+)$')
FIVE_TO_PATTERN = re.compile(r'five(?:~minutes)?~(?:to|till)~(?P<rest>.+)$')
FIVE_PAST_PATTERN = re.compile(r'five(?:~minutes)?~(?:past|after)~(?P<rest>.+)$')
CLOCK_TIME_PATTERN = re.compile(r'(?P<hours>\d{1,2})(?::(?P<minutes>\d{1,2}))?$')


HOURS = {
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
    'ten': 10,
    'eleven': 11,
    'twelve': 12,
}


MINUTES = {
    '~one': 1,
    '~two': 2,
    '~three': 3,
    '~four': 4,
    '~five': 5,
    '~six': 6,
    '~seven': 7,
    '~eight': 8,
    '~nine': 9,
    '~ten': 10,
    '~eleven': 11,
    '~twelve': 12,
    '~thirteen': 13,
    '~fourteen': 14,
    '~fifteen': 15,
    '~sixteen': 16,
    '~seventeen': 17,
    '~eighteen': 18,
    '~nineteen': 19,
    '~twenty': 20,
    '~twenty-one': 21,
    '~twenty-two': 22,
    '~twenty-three': 23,
    '~twenty-four': 24,
    '~twenty-five': 25,
    '~twenty-six': 26,
    '~twenty-seven': 27,
    '~twenty-eight': 28,
    '~twenty-nine': 29,
    '~thirty': 30,
    '~thirty-one': 31,
    '~thirty-two': 32,
    '~thirty-three': 33,
    '~thirty-four': 34,
    '~thirty-five': 35,
    '~thirty-six': 36,
    '~thirty-seven': 37,
    '~thirty-eight': 38,
    '~thirty-nine': 39,
    '~fourty': 40,
    '~fourty-one': 41,
    '~fourty-two': 42,
    '~fourty-three': 43,
    '~fourty-four': 44,
    '~fourty-five': 45,
    '~fourty-six': 46,
    '~fourty-seven': 47,
    '~fourty-eight': 48,
    '~fourty-nine': 49,
    '~fifty': 50,
    '~fifty-one': 51,
    '~fifty-two': 52,
    '~fifty-three': 53,
    '~fifty-four': 54,
    '~fifty-five': 55,
    '~fifty-six': 56,
    '~fifty-seven': 57,
    '~fifty-eight': 58,
    '~fifty-nine': 59,
    '-one': 1,
    '-two': 2,
    '-three': 3,
    '-four': 4,
    '-five': 5,
    '-six': 6,
    '-seven': 7,
    '-eight': 8,
    '-nine': 9,
    '-ten': 10,
    '-eleven': 11,
    '-twelve': 12,
    '-thirteen': 13,
    '-fourteen': 14,
    '-fifteen': 15,
    '-sixteen': 16,
    '-seventeen': 17,
    '-eighteen': 18,
    '-nineteen': 19,
    '-twenty': 20,
    '-twenty-one': 21,
    '-twenty-two': 22,
    '-twenty-three': 23,
    '-twenty-four': 24,
    '-twenty-five': 25,
    '-twenty-six': 26,
    '-twenty-seven': 27,
    '-twenty-eight': 28,
    '-twenty-nine': 29,
    '-thirty': 30,
    '-thirty-one': 31,
    '-thirty-two': 32,
    '-thirty-three': 33,
    '-thirty-four': 34,
    '-thirty-five': 35,
    '-thirty-six': 36,
    '-thirty-seven': 37,
    '-thirty-eight': 38,
    '-thirty-nine': 39,
    '-fourty': 40,
    '-fourty-one': 41,
    '-fourty-two': 42,
    '-fourty-three': 43,
    '-fourty-four': 44,
    '-fourty-five': 45,
    '-fourty-six': 46,
    '-fourty-seven': 47,
    '-fourty-eight': 48,
    '-fourty-nine': 49,
    '-fifty': 50,
    '-fifty-one': 51,
    '-fifty-two': 52,
    '-fifty-three': 53,
    '-fifty-four': 54,
    '-fifty-five': 55,
    '-fifty-six': 56,
    '-fifty-seven': 57,
    '-fifty-eight': 58,
    '-fifty-nine': 59,
}


def guess_clock_time(string, delta_h=0, delta_m=0, assume='pm'):
    if string == 'midnight':
        return '00:00'
    if string in ('noon', 'midday'):
        return '12:00'
    match = AM_PATTERN.match(string)
    if match:
        return guess_clock_time(match.group('rest'), assume='am')
    match = PM_PATTERN.match(string)
    if match:
        return guess_clock_time(match.group('rest'), assume='pm')
    for suffix in ("~o'clock",):
        if string.endswith(suffix):
            return guess_clock_time(string[:-len(suffix)], assume=assume)
    match = QUARTER_TO_PATTERN.match(string)
    if match:
        return guess_clock_time(match.group('rest'), delta_h=-1, delta_m=45, assume=assume)
    match = QUARTER_PAST_PATTERN.match(string)
    if match:
        return guess_clock_time(match.group('rest'), delta_m=15, assume=assume)
    match = HALF_PAST_PATTERN.match(string)
    if match:
        return guess_clock_time(match.group('rest'), delta_m=30, assume=assume)
    match = FIVE_TO_PATTERN.match(string)
    if match:
        return guess_clock_time(match.group('rest'), delta_h=-1, delta_m=55, assume=assume)
    match = FIVE_PAST_PATTERN.match(string)
    if match:
        return guess_clock_time(match.group('rest'), delta_m=5, assume=assume)
    for suffix in MINUTES:
        if string.endswith(suffix):
            return guess_clock_time(string[:-len(suffix)], delta_m=MINUTES[suffix], assume=assume)
    if string in HOURS:
        return clock_time(HOURS[string] + delta_h, delta_m, assume)
    match = CLOCK_TIME_PATTERN.match(string)
    if match:
        hours = int(match.group('hours')) + delta_h
        if match.group('minutes') is None:
            minutes = delta_m
        else:
            minutes = int(match.group('minutes'))
        return clock_time(hours, minutes, assume)
    return string


def clock_time(h, m, assume):
    if h < 12 and assume == 'pm':
        h += 12
    return '{:02d}:{:02d}'.format(h, m)


### DAY OF MONTH ##############################################################


DAYS = {
    'first': 1,
    'second': 2,
    'third': 3,
    'fourth': 4,
    'fifth': 5,
    'sixth': 6,
    'seventh': 7,
    'eighth': 8,
    'ninth': 9,
    'tenth': 10,
    'eleventh': 11,
    'twelfth': 12,
    'thirteenth': 13,
    'fourteenth': 14,
    'fifteenth': 15,
    'sixteenth': 16,
    'seventeenth': 17,
    'eighteenth': 18,
    'nineteenth': 19,
    'twentieth': 20,
    'twenty-first': 21,
    'twenty-second': 22,
    'twenty-third': 23,
    'twenty-fourth': 24 ,
    'twenty-fifth': 25,
    'twenty-sixth': 26,
    'twenty-seventh': 27,
    'twenty-eighth': 28,
    'twenty-ninth': 29,
    'thirtieth': 30,
    'thirty-first': 31,
    '1': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    '10': 10,
    '11': 11,
    '12': 12,
    '13': 13,
    '14': 14,
    '15': 15,
    '16': 16,
    '17': 17,
    '18': 18,
    '19': 19,
    '20': 20,
    '21': 21,
    '22': 22,
    '23': 23,
    '24': 24,
    '25': 25,
    '26': 26,
    '27': 27,
    '28': 28,
    '29': 29,
    '30': 30,
    '31': 31,
    '1st': 1,
    '2nd': 2,
    '3rd': 3,
    '4th': 4,
    '5th': 5,
    '6th': 6,
    '7th': 7,
    '8th': 8,
    '9th': 9,
    '10th': 10,
    '11th': 11,
    '12th': 12,
    '13th': 13,
    '14th': 14,
    '15th': 15,
    '16th': 16,
    '17th': 17,
    '18th': 18,
    '19th': 19,
    '20th': 20,
    '21st': 21,
    '22nd': 22,
    '23rd': 23,
    '24th': 24,
    '25th': 25,
    '26th': 26,
    '27th': 27,
    '28th': 28,
    '29th': 29,
    '30th': 30,
    '31st': 31,
}


def guess_day_of_month(string):
    if string in DAYS:
        return '{:02d}'.format(DAYS[string])
    return string


### DAY OF WEEK ###############################################################


def guess_day_of_week(string):
    return string


### MONTH OF YEAR #############################################################


MONTHS = {
    'january': 1,
    'february': 2,
    'march': 3,
    'april': 4,
    'may': 5,
    'june': 6,
    'july': 7,
    'august': 8,
    'september': 9,
    'october': 10,
    'november': 11,
    'december': 12,
}


def guess_month_of_year(string):
    if string in MONTHS:
        return '{:02d}'.format(MONTHS[string])
    return string


### YEAR OF CENTURY ###########################################################


DECADE_PATTERN = re.compile(r'(?P<century>\d{1,2})(?P<decade>\d)0s')


def guess_year_of_century(string):
    match = DECADE_PATTERN.match(string)
    if match:
        return '{:02d}{}X'.format(int(match.group('century')), match.group('decade'))
    return string


### HELPERS ###################################################################


def unquote(string):
    assert string.startswith('"')
    assert string.endswith('"')
    return string[1:-1]


def quote(string):
    return '"' + string + '"'
