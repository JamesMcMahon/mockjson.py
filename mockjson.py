#!/usr/bin/env python

import json
import random
import re
import string
import types

# FIXME should this be tuples or list?
data = {
    'NUMBER' : tuple("0123456789"),
    'LETTER_UPPER' : tuple(string.uppercase),
    'LETTER_LOWER' : tuple(string.lowercase),
    'MALE_FIRST_NAME' : ["James", "John", "Robert", "Michael", "William", "David",
        "Richard", "Charles", "Joseph", "Thomas", "Christopher", "Daniel", 
        "Paul", "Mark", "Donald", "George", "Kenneth", "Steven", "Edward",
        "Brian", "Ronald", "Anthony", "Kevin", "Jason", "Matthew", "Gary",
        "Timothy", "Jose", "Larry", "Jeffrey", "Frank", "Scott", "Eric"],
    'FEMALE_FIRST_NAME' : ["Mary", "Patricia", "Linda", "Barbara", "Elizabeth", 
        "Jennifer", "Maria", "Susan", "Margaret", "Dorothy", "Lisa", "Nancy", 
        "Karen", "Betty", "Helen", "Sandra", "Donna", "Carol", "Ruth", "Sharon",
        "Michelle", "Laura", "Sarah", "Kimberly", "Deborah", "Jessica", 
        "Shirley", "Cynthia", "Angela", "Melissa", "Brenda", "Amy", "Anna"], 
    'LAST_NAME' : ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller",
        "Davis", "Garcia", "Rodriguez", "Wilson", "Martinez", "Anderson",
        "Taylor", "Thomas", "Hernandez", "Moore", "Martin", "Jackson",
        "Thompson", "White", "Lopez", "Lee", "Gonzalez", "Harris", "Clark",
        "Lewis", "Robinson", "Walker", "Perez", "Hall", "Young", "Allen"]
}


def random_data(key) :
    key = key.lstrip('@')

    params = re.search(r"\(([^\)]+)\)/g", key)
    params = params.groups() if params else []

    if not data.has_key(key):
        return key #FIXME log or exception

    d = data[key]
    k_type = type(d)
    if k_type is list or k_type is tuple:
        return d[random.randint(0, len(d))]
    elif k_type is types.FunctionType:
        return d
    raise Exception('invalid key type')


def generate_json(template, name=None):
    #print template, name

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
            stripped_key = re.sub(r"\|(\d+-\d+|\+\d+)",'', key) 
            generated[stripped_key] = generate_json(value, key)
            
            # handle increments
            inc_matches = re.search(r"\w+\|\+(\d+)", key)
            if inc_matches and type(template[key]) is int:
                increment = int(inc_matches.groups()[0])
                template[key] += increment
    elif t_type is list:
        generated = []
        for i in range(length):
            generated.append(generate_json(template[0]))
    elif t_type is int:
        generated = length if matches else template
    elif t_type is bool:
        # apparently getrandbits(1) is faster...
        generated = random.choice([True, False]) if matches else template
    # is this always just going to be unicode here?
    elif t_type is str or t_type is unicode:
        if template:
            generated = ''
            length = length if length else 1
            for i in range(length):
                generated += template
            print 'generated', generated
            matches = re.search(r"@([A-Z_0-9\(\),]+)/g", generated)
            # FIXME this is never matching, regex is broken
            print 'matches', matches
            if matches:
                for key in matches.groups():
                    generated = generated.replace(key, random_data(key))
        else:
            generated = ''.join(random.choice(string.letters) for i in xrange(length))

    else:
        generated = template

    return generated

if __name__ == '__main__':
    with open('test.template.json') as f:
        json_data = json.load(f)
    print(json.dumps(generate_json(json_data), sort_keys=False))
