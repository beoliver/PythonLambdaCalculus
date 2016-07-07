#!/usr/bin/env python
import sys

def tokenize(x):
    # """
    # convert a string literal (eg. r"(\x. x x) y") into a list of tokens
    # ["(", "\\", "x", ".", "x", "x", ")", "y", ")"]
    # no real need to use regex as we only have 4 special characters!
    # """
    y = x.replace('.',' . ').replace('(',' ( ').replace(')',' ) ').replace('\\',' \\ ')
    return y.split()


def parens_to_lists(xs):
    """
    used to create an initial nested list from tokenized input
    """
    stack = [[]]
    for x in xs:
        if x == '(':
            stack[-1].append([])
            stack.append(stack[-1][-1])
        elif x == ')':
            stack.pop()
            if not stack:
                return []
        else:
            stack[-1].append(x)
    if len(stack) > 1:
        return []
    k = stack.pop()
    return k.pop() if len(k) == 1 else k


def explicit_sublists(xs):
    """
    make application and lambda abstraction explicit
    """
    # var case
    if type(xs) != list:
        return xs
    if len(xs) > 3 and xs[2] == '.':
        # lambda abstraction case
        return xs[:3] + [explicit_sublists(xs[3:])]
    else:
        if "\\" in xs:
            # we need to enclose the occurrences of lambda
            # eg. "x \y . y" where the lamba is in some arbitrary position
            for (i,x) in enumerate(xs):
                if x == '\\': # find the first occurrence (recursive)
                    xs = xs[:i] + [explicit_sublists(xs[i:])]
        # we now reduce turning [x, y, z] into [[x, y], z]
        return reduce(lambda x,y: [x] + [y], [explicit_sublists(x) for x in xs])


######################################################################################

def parse(xs):
    return explicit_sublists(parens_to_lists(tokenize(xs)))

def parsed_to_string(xs):
    if type(xs) == list:
        return '(' + ' '.join(parsed_to_string(x) for x in xs) + ')'
    else:
        return xs

######################################################################################

def tests():
    t1 = r'(\x. \y. \z. x y z) t'
    print(t1)
    print(parsed_to_string(parse(t1)))
    print "***************************************"
    t2 = r'\x. \y. \z. x y z'
    print(t2)
    print(parsed_to_string(parse(t2)))
    print "***************************************"
    t3 = r'\x. \y. x y \z . z x'
    print(t3)
    print(parsed_to_string(parse(t3)))
    print "***************************************"

if __name__ == '__main__':
    try:
        input = sys.argv[1]
        print parsed_to_string(parse(input))
    except IndexError:
        print "pass a lambda expression eg. \'\\x. x x x\'"
