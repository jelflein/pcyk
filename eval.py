
from argparse import ArgumentParser

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
                    lp = ... # your code (labelled precision)
                    lr = ... # your code (labelled recall)
                    print(lp, lr, parsed[1], gold, sep='\t', flush=True)
                    sum_lp += lp
                    sum_lr += lr
                    total += 1
                else:
                    print('No parse found for "{}"'.format(' '.join(tokens)), file=sys.stderr)
    print('Average LP =', sum_lp / total, file=sys.stderr)
    print('Average LR =', sum_lr / total, file=sys.stderr)
    print('Anzahl =', total, file=sys.stderr)

if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument('--rules', type=str, default='old_rules.txt')
    ap.add_argument('--lexicon', type=str, default='lexicon.txt')
    ap.add_argument('--beam', type=int, default=0)
    ap.add_argument('--maxlen', type=int, default=0)
    ap.add_argument('trees')
    eval(ap.parse_args())
