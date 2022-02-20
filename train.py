import argparse
import math
import sys

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from tree import parse_string, Tree

quantity_rules = defaultdict(int)
left_quantity = defaultdict(int)
words = defaultdict(int)

rules = set()
lexicon = set()
used_terminals = defaultdict(int)


def train(args):
    # args.trees = Dateiname der Baumbank
    with open(args.trees) as f:
        trees = [parse_string(line) for line in f]

        for tree in trees:
            compute_rule(tree)

    compute_ovv()
    binarization()

    # args.rules = Name der Datei, in der die (nicht-lexikalischen)
    #   Regeln gespeichert werden sollen
    # args.lexicon = Name der Datei, in der die lexikalischen Regeln
    #   gespeichert werden sollen
    with open(args.rules, 'w') as fr:
        for rule in rules:
            left_part = rule.split(" -> ")[0]
            assert quantity_rules[rule] > 0

            prob = math.log(quantity_rules[rule] / left_quantity[left_part])
            #prob = quantity_rules[rule] / left_quantity[left_part]

            fr.write(rule + "\t" + str(prob) + "\n")

    with open(args.lexicon, 'w') as fl:
        for lexicon_entry in lexicon:
            print(lexicon_entry)
            left_part = lexicon_entry.split(" -> ")[0]

            assert quantity_rules[lexicon_entry] > 0

            prob = math.log(quantity_rules[lexicon_entry] / left_quantity[left_part])
            #prob = quantity_rules[lexicon_entry] / left_quantity[left_part]

            fl.write(lexicon_entry + "\t" + str(prob) + "\n")


# Your code: Regeln und Lexikon zusammen mit (Log-)
# Wahrscheinlichkeiten ausgeben / speichern.

def compute_rule(tree: Tree):
    agenda = [tree]

    while len(agenda) != 0:
        cur_tree = agenda.pop()

        is_lexicon_entry = False
        rule = cur_tree.label + " ->"
        left_quantity[cur_tree.label] += 1

        for children_tree in cur_tree.children:
            rule += " " + children_tree.label

            if len(children_tree.children) > 0:
                agenda.append(children_tree)
            else:
                is_lexicon_entry = True
                words[children_tree.label] += 1

        quantity_rules[rule] += 1

        if is_lexicon_entry:
            lexicon.add(rule)
        else:
            rules.add(rule)


def binarization():
    for rule in set(rules):
        left, right = rule.split(" -> ")
        right_terminals = right.split()

        # NP -> DET NP ADJA XY DD ASD
        if len(right_terminals) <= 2:
            continue

        # print(rule)
        new_rules = truncate(left, right_terminals)

        for i in range(0, len(new_rules)):
            new_rule = new_rules[i]

            if i == len(new_rules) - 1:
                quantity_rules[new_rules[-1]] = quantity_rules[rule]
            else:
                assert new_rule not in quantity_rules
                quantity_rules[new_rule] = 1

            rules.add(new_rule)

        rules.remove(rule)


def get_terminal_name(first_part, second_part):
    new_terminal = first_part + "+" + second_part
    used_terminals[new_terminal] += 1

    new_terminal += str(used_terminals[new_terminal]) + "'"
    left_quantity[new_terminal] += 1

    return new_terminal


# S -> A B C D E
# S -> AB' CD'
# AB' -> A B
# CD' -> C D
def truncate(left_part, rules):
    agenda = [(left_part, rules, [])]
    new_rules = []

    while len(agenda) != 0:
        rule_fragment = agenda.pop()

        left = rule_fragment[1]
        right = rule_fragment[2]

        if len(right) == 0 and len(left) > 2:
            new_terminal = get_terminal_name(left[0], left[1])

            agenda.append((rule_fragment[0], new_terminal, left[-1]))
            agenda.append((new_terminal, left[:len(left) - 1], []))
        else:
            if isinstance(left, list):
                if len(left) > 0:
                    rule_fragment = (rule_fragment[0], " ".join(left), rule_fragment[2])
                else:
                    rule_fragment = (rule_fragment[0], "", rule_fragment[2])

            if isinstance(right, list):
                if len(right) > 0:
                    rule_fragment = (rule_fragment[0], rule_fragment[1], right[0])
                else:
                    rule_fragment = (rule_fragment[0], rule_fragment[1], "")

            if rule_fragment[2] == "":
                new_rules.append(rule_fragment[0] + " -> " + rule_fragment[1])
            else:
                new_rules.append(rule_fragment[0] + " -> " + rule_fragment[1] + " " + rule_fragment[2])

            #print(rule_fragment[0] + " -> " + rule_fragment[1] + " " + rule_fragment[2])

    return new_rules


def compute_ovv():
    global lexicon
    for lexicon_entry in set(lexicon):
        split = lexicon_entry.split(" -> ")

        if words[split[1]] == 1:
            lexicon.remove(lexicon_entry)

            new_rule = split[0] + " -> " + "OOV"
            lexicon.add(new_rule)

            quantity_rules[new_rule] += quantity_rules[lexicon_entry]
            quantity_rules[lexicon_entry] -= 1

            if quantity_rules[lexicon_entry] == 0:
                del quantity_rules[lexicon_entry]


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--rules', type=str, default='rules.txt')
    ap.add_argument('--lexicon', type=str, default='lexicon.txt')
    ap.add_argument('trees', type=str)

    #truncate("S", ["A", "B", "C", "D", "E", "F", "G", "W"], "S - A B C")
    train(ap.parse_args())

'''
( S ( NP ( Det die ) ( N Studentin ) ) ( VP ( V arbeitet ) )



'''
