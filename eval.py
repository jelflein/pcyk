from argparse import ArgumentParser
from collections import defaultdict

from tree import parse_string

from pcyk import PCYK

import sys


def eval(args):
    parser = PCYK(args.rules, args.lexicon, args.beam)
    sum_lp = 0
    sum_lr = 0
    total = 0
    with open(args.trees) as f:
        for line in f:
            gold = parse_string(line)
            tokens = [node.label for node in gold.terminals()]
            if args.maxlen and len(tokens) <= args.maxlen:
                parsed = parser.parse(tokens)
                if parsed:
                    parsed_tree = parsed[1]
                    print(parsed_tree)
                    unbinary_tree(parsed_tree)

                    correct_constitues = correct_constitue(parsed_tree, gold)
                    lp = correct_constitues / len(parsed_tree.nonterminals())
                    lr = correct_constitues / len(gold.nonterminals())

                    print(lp, lr, parsed_tree, gold, sep='\t', flush=True)
                    sum_lp += lp
                    sum_lr += lr
                    total += 1
                else:
                    print('No parse found for "{}"'.format(' '.join(tokens)), file=sys.stderr)
    print('Average LP =', sum_lp / total, file=sys.stderr)
    print('Average LR =', sum_lr / total, file=sys.stderr)
    print('Anzahl =', total, file=sys.stderr)


def correct_constitue(unbinary_tree, gold):
    eval_set = compute_eval_set(gold)

    agenda = [unbinary_tree]

    lp = 0
    while len(agenda) > 0:
        c_tree = agenda.pop()

        con = ""
        for child in c_tree.children:
            con += str(child)

        if (c_tree.label, con) in eval_set:
            lp += 1

        agenda.extend(c_tree.children)

    return lp


def compute_eval_set(tree):
    eval_set = set()

    agenda = [tree]

    while len(agenda) > 0:
        c_tree = agenda.pop()

        con = ""
        for child in c_tree.children:
            con += str(child)

        if con != "":
            eval_set.add((c_tree.label, con))

        agenda.extend(c_tree.children)

    return eval_set


def unbinary_tree(tree):
    agenda = [tree]

    while len(agenda) > 0:
        c_tree = agenda.pop()
        # print(c_tree)

        new_children_agenda = []
        new_children_agenda.extend(c_tree.children)
        new_children = []

        while len(new_children_agenda) > 0:
            new_child = new_children_agenda.pop()

            if new_child.is_binary():
                new_children_agenda.extend(new_child.children)
            else:
                new_children.append(new_child)

        new_children.reverse()
        c_tree.children = new_children

        agenda.extend(c_tree.children)


if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument('--rules', type=str, default='rules.txt')
    ap.add_argument('--lexicon', type=str, default='lexicon.txt')
    ap.add_argument('--beam', type=int, default=100)
    ap.add_argument('--maxlen', type=int, default=25)
    ap.add_argument('trees')
    eval(ap.parse_args())
