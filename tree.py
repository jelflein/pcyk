import re

token_re = re.compile("(\(|\)|[^()\s]+)")
binary_label = re.compile("(.+)\+(.+)'")


class Tree:
    def __init__(self, label, children):
        self.label = label
        self.children = children

    def __str__(self):
        if self.children:
            return '(%s %s)' % (self.label, ' '.join(str(child) for child in self.children))
        else:
            return self.label

    def __repr__(self):
        return 'Tree(%r, %r)' % (self.label, self.children)

    def __eq__(self, other):
        return self.label == other.label and self.children == other.children

    def __iter__(self):
        return TreeIterator(self)

    def terminals(self):
        return [node for node in self if node.is_terminal()]

    def preterminals(self):
        return [node for node in self if node.is_preterminal()]

    def nonterminals(self):
        return [node for node in self if node.is_nonterminal()]

    def is_nonterminal(self):
        return len(self.children) > 0

    def is_preterminal(self):
        return len(self.children) == 1 and self.children[0].is_terminal()

    def is_terminal(self):
        return self.children == []

    def is_binary(self):
        return binary_label.fullmatch(self.label)

    def non_terminals_without_binary(self):
        return [node for node in TreeBinIterator(self) if node.is_nonterminal()]


class TreeIterator:
    def __init__(self, tree):
        self.agenda = [tree]

    def __iter__(self):
        return self

    def __next__(self):
        if self.agenda == []:
            raise StopIteration
        current = self.agenda.pop()
        for child in reversed(current.children):
            self.agenda.append(child)
        return current


class TreeBinIterator:
    def __init__(self, tree):
        self.agenda = [tree]

    def __iter__(self):
        return self

    def __next__(self):
        if self.agenda == []:
            raise StopIteration
        current = self.agenda.pop()
        for child in reversed(current.children):
            if child.is_binary:
                self.agenda.extend(child.children)
            else:
                self.agenda.append(child)
        return current


class ParseError(Exception):
    pass


def tree(token, rest):
    if token == ')':
        raise ParseError
    elif token == '(':
        return Tree(next(rest), trees(rest))
    else:
        return Tree(token, [])


def trees(tokens):
    result = []
    for token in tokens:
        if token == ')':
            return result
        result.append(tree(token, tokens))
    raise ParseError


def parse_string(string):
    if string == '':
        raise ParseError

    #    tokens = iter()
    tokens = iter(token_re.findall(string))
    result = tree(next(tokens), tokens)
    # Stelle sicher, dass die Eingabe komplett eingelesen wurde
    try:
        next(tokens)
    except StopIteration:
        return result
    else:
        raise ParseError


class parse_file:
    def __init__(self, file):
        self.tokens = tokenize_file(file)

    def __iter__(self):
        return self

    def __next__(self):
        return tree(next(self.tokens), self.tokens)


class parse_wsj:
    def __init__(self, file):
        self.tokens = tokenize_file(file)

    def __iter__(self):
        return self

    def __next__(self):
        if next(self.tokens) != '(':
            raise ParseError
        result = []
        for token in self.tokens:
            if token == ')':
                return result
            result.append(tree(token, self.tokens))
        raise StopIteration


class tokenize_file:
    def __init__(self, file):
        self.file = file
        self.buffer = []

    def __iter__(self):
        return self

    def __next__(self):
        while self.buffer == []:
            self.buffer = re.findall(r'(\(|\)|[^()\s]+)', next(self.file))
        return self.buffer.pop(0)
