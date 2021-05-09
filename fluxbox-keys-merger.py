#!/usr/bin/python3


import os
from argparse import ArgumentParser

POSSIBLE_MODIFIERS = ["control", "shift", "mod1", "mod4", "mod2", "mod3", "lock", "ondesktop", "ontoolbar", "onwindow", "ontitlebar", "ontab", "onleftgrip", "onrightgrip", "double", "none"]

class Mapping(object):
    def __init__(self):
        self.key = None
        self.modifiers = []
        self.comments = []
        self.command = ""
    def __repr__(self):
        return '{} {}: {}'.format(' '.join(self.modifiers), self.key, self.command)
    def matchesCombo(self, other):
        return self.key == other.key and self.modifiers == other.modifiers

def parse(filename):
    mappings = []
    lines = None
    with open(filename) as f:
        lines = f.readlines()
    comments = []
    for line in lines:
        #  print('Comments: ' + repr(comments))
        line = line.strip()
        if line.startswith('#') or line.startswith('!') or line.startswith('-'):
            comments.append(line)
        elif len(line) == 0:
            comments.append("")
        else:
            mods = []
            key = None
            while len(line) > 0:
                line = line.strip()
                isModifier = False
                for possibleModifier in POSSIBLE_MODIFIERS:
                    if line.lower().startswith(possibleModifier):
                        isModifier = True
                part = line[0:line.find(' ')]
                line = line[line.find(' '):]
                if isModifier:
                    mods.append(part)
                else:
                    key = part
                    break
            mapping = Mapping()
            mapping.key = key
            mapping.modifiers = mods
            mapping.command = line[line.find(':') + 1:]
            mapping.comments = comments[:]
            comments.clear()
            mappings.append(mapping)
    return mappings

def merge(original, additions, allow_duplicate_command_mappings=False):
    original, additions = additions, original
    result = original
    for addition in additions:
        matchesCombo = False
        for mapping in original:
            if mapping.matchesCombo(addition) and mapping.command != addition.command:
                matchesCombo = True
        matchesCommand = False
        for mapping in original:
            if not mapping.matchesCombo(addition) and mapping.command == addition.command:
                matchesCommand = True
        #  print('Combo Match: {}, Command Match: {}'.format(matchesCombo, matchesCommand))
        if matchesCombo:
            continue
        elif matchesCommand:
            if allow_duplicate_command_mappings:
                result.append(addition)
            continue
        else:
            result.append(addition)
    return result


parser = ArgumentParser()
parser.add_argument('original', type=str)
parser.add_argument('additional', type=str)
parser.add_argument('output', type=str)

args = parser.parse_args()

mappingsOriginal = parse(args.original)
mappingsAdditions = parse(args.additional)

result = merge(mappingsOriginal, mappingsAdditions, allow_duplicate_command_mappings=True)

with open(args.output, 'w') as f:
    for mapping in result:
        for line in mapping.comments:
            f.write(line + '\n')
        f.write(repr(mapping) + '\n')



