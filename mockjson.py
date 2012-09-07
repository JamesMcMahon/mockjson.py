#!/usr/bin/env python

"""mockjson.py: Library for mocking JSON objects from a template."""

__author__ = "James McMahon"
__copyright__ = "Copyright 2012, James McMahon"
__license__ = "MIT"

try:
    import simplejson as json
except ImportError:
    import json
import random
import re
import string
import sys

from datetime import datetime, timedelta

_male_first_name = """James John Robert Michael William David
    Richard Charles Joseph Thomas Christopher Daniel
    Paul Mark Donald George Kenneth Steven Edward
    Brian Ronald Anthony Kevin Jason Matthew Gary
    Timothy Jose Larry Jeffrey Frank Scott Eric""".split()
_female_first_name = """Mary Patricia Linda Barbara Elizabeth
    Jennifer Maria Susan Margaret Dorothy Lisa Nancy
    Karen Betty Helen Sandra Donna Carol Ruth Sharon
    Michelle Laura Sarah Kimberly Deborah Jessica
    Shirley Cynthia Angela Melissa Brenda Amy Anna""".split()
_last_name = """Smith Johnson Williams Brown Jones Miller
    Davis Garcia Rodriguez Wilson Martinez Anderson
    Taylor Thomas Hernandez Moore Martin Jackson
    Thompson White Lopez Lee Gonzalez Harris Clark
    Lewis Robinson Walker Perez Hall Young Allen""".split()
_lorem = """lorem ipsum dolor sit amet consectetur adipisicing elit
    sed do eiusmod tempor incididunt ut labore et dolore magna aliqua
    Ut enim ad minim veniam quis nostrud exercitation ullamco laboris
    nisi ut aliquip ex ea commodo consequat Duis aute irure dolor in
    reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
    pariatur Excepteur sint occaecat cupidatat non proident sunt in
    culpa qui officia deserunt mollit anim id est laborum""".split()


def _random_data(key):
    if not key in data:
        return key
    return data[key]()


def _lorem_ipsum():
    length = random.randrange(2, len(_lorem) / 2)
    return ' '.join(random.choice(_lorem) for _ in xrange(length))


def _random_date():
    return datetime.today() - timedelta(days=random.randrange(6571, 27375))

data = dict(
    NUMBER=lambda: random.choice(string.digits),
    LETTER_UPPER=lambda: random.choice(string.uppercase),
    LETTER_LOWER=lambda: random.choice(string.lowercase),
    MALE_FIRST_NAME=lambda: random.choice(_male_first_name),
    FEMALE_FIRST_NAME=lambda: random.choice(_female_first_name),
    LAST_NAME=lambda: random.choice(_last_name),
    EMAIL=lambda: (_random_data('LETTER_LOWER')
                      + '.'
                      + _random_data('LAST_NAME').lower()
                      + '@'
                      + _random_data('LAST_NAME').lower()
                      + '.com'),
    LOREM=lambda: random.choice(_lorem),
    LOREM_IPSUM=_lorem_ipsum,
    DATE_YYYY=lambda: str(_random_date().year),
    DATE_MM=lambda: str(_random_date().month).zfill(2),
    DATE_DD=lambda: str(_random_date().day).zfill(2),
    TIME_HH=lambda: str(_random_date().hour).zfill(2),
    TIME_MM=lambda: str(_random_date().minute).zfill(2),
    TIME_SS=lambda: str(_random_date().second).zfill(2)
)


def generate_json_object(template, name=None):
    length = 0
    if name:
        matches = re.search(r"\w+\|(\d+)-(\d+)", name)
        if matches:
            groups = matches.groups()
            length_min = int(groups[0])
            length_max = int(groups[1])
            length = random.randint(length_min, length_max)

    t_type = type(template)
    if t_type is dict:
        generated = {}
        for key, value in template.iteritems():
            stripped_key = re.sub(r"\|(\d+-\d+|\+\d+)", '', key)
            generated[stripped_key] = generate_json_object(value, key)

            # handle increments
            inc_matches = re.search(r"\w+\|\+(\d+)", key)
            if inc_matches and type(template[key]) is int:
                increment = int(inc_matches.groups()[0])
                template[key] += increment
    elif t_type is list:
        generated = []
        for i in xrange(length):
            generated.append(generate_json_object(template[0]))
    elif t_type is int:
        generated = length if matches else template
    elif t_type is bool:
        # apparently getrandbits(1) is faster...
        generated = random.choice([True, False]) if matches else template
    # is this always just going to be unicode here?
    elif t_type is str or t_type is unicode:
        if template:
            length = length if length else 1
            generated = ''.join(template for _ in xrange(length))
            matches = re.findall(r"(@[A-Z_0-9\(\),]+)", generated)
            if matches:
                for key in matches:
                    rd = _random_data(key.lstrip('@'))
                    generated = generated.replace(key, rd, 1)
        else:
            generated = (''.join(random.choice(string.letters)
                         for i in xrange(length)))
    else:
        generated = template
    return generated


def generate_json(template):
    return json.dumps(generate_json_object(json_data), sort_keys=True, indent=4)


if __name__ == '__main__':
    arg = sys.argv[1:][0]
    with open(arg) as f:
        json_data = json.load(f)
    print(generate_json(json_data))
