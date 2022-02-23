import sys

from argparse import ArgumentParser

from collections import defaultdict

from tree import Tree


def load_lexicon(filename):
    # Platzhalter; hier soll das Lexikon eingelesen werden.

    lexicon = defaultdict(list)

    with open(filename, 'r') as fl:
        for line in fl:
            # [word, word\tprob]
            split = line.strip().split(" -> ")

            left_part = split[0]

            split = split[1].split("\t")
            right_part = split[0]

            prob = split[1]

            lexicon[right_part].append((float(prob), left_part))

    return lexicon


def load_rules(filename):
    rules = defaultdict(lambda: defaultdict(list))
    with open(filename, 'r') as fl:
        for line in fl:
            # [word, word\tprob]
            split = line.strip().split(" -> ")

            left_terminal = [split[0]][0]

            split = split[1].split("\t")

            right_terminals = split[0].split()
            prob = split[len(split) - 1]

            rules[right_terminals[0]][right_terminals[1]].append((float(prob), left_terminal))

    return rules


class PCYK():
    def __init__(self, rules, lexicon, beam):
        self.rules = load_rules(rules)
        self.lexicon = load_lexicon(lexicon)
        # maximale Anzahl an Konstituenten, die in den Zellen der Chart gespeichert 
        # werden sollen. 
        self.beam = beam

    def parse(self, tokens):
        P = defaultdict(dict)  # Wahrscheinlichkeiten
        B = defaultdict(dict)  # Bäume
        for i, wi in enumerate(tokens, start=1):
            for prob, lhs in self.lexicon.get(wi, []) or self.lexicon['OOV']:  # nimm "OOV" falls wi nicht im Lexikon
                P[i - 1, i][lhs] = prob
                B[i - 1, i][lhs] = Tree(lhs, [Tree(wi, [])])

            for j in range(i - 2, -1, -1):
                for k in range(j + 1, i):
                    for rhs1 in P[j, k]:
                        for rhs2 in P[k, i]:
                            for ruleprob, lhs in self.rules[rhs1][rhs2]:
                                prob = ruleprob + P[j, k][rhs1] + P[k, i][rhs2]
                                if lhs not in P[j, i] or prob > P[j, i][lhs]:
                                    if len(P[j, i]) > self.beam:
                                        min_key = max(P[j, i], key=P[j, i].get)

                                        if prob < P[j, i][min_key]:
                                            continue

                                        del P[j, i][min_key]
                                        del B[j, i][min_key]

                                    # update Wahrscheinlichkeit
                                    P[j, i][lhs] = prob
                                    # update Pointer / Baum
                                    B[j, i][lhs] = Tree(lhs, [B[j, k][rhs1], B[k, i][rhs2]])

        if "S" in P[0, i]:
            return (P[0, i]["S"], B[0, i]["S"])
        else:
            return None


def main(args):
    parser = PCYK(args.rules, args.lexicon, args.beam)
    with open(args.file) as f:
        for tokens in f:
            tokens = tokens.split()
            if args.maxlen and len(tokens) <= args.maxlen:
                result = parser.parse(tokens)
                if result:
                    print(*result, sep='\t')
                else:
                    print('No parse found for "{}"'.format(' '.join(tokens)), file=sys.stderr)


if __name__ == "__main__":
    ap = ArgumentParser()
    ap.add_argument('--rules', type=str, default='rules.txt')
    ap.add_argument('--lexicon', type=str, default='lexicon.txt')
    ap.add_argument('--beam', type=int, default=50)
    ap.add_argument('--maxlen', type=int, default=25)
    ap.add_argument('file')
    main(ap.parse_args())
