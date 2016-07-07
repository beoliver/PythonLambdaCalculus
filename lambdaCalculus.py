#!/usr/bin/env python

import logging, sys, itertools

# a simple set of functions that can read lambda expressions as string literals.
# The "interal" representation of lambda expressions avoids classes and just
# uses nested lists.

######################################################################################

def tokenize(x):
    # convert a string literal (eg. r"(\x. x x) y") into a list of tokens
    # ["(", "\\", "x", ".", "x", "x", ")", "y", ")"]
    # no real need to use regex as we only have 4 special characters!
    y = x.replace('.',' . ').replace('(',' ( ').replace(')',' ) ').replace('\\',' \\ ')
    return y.split()

######################################################################################

def parens_to_lists(xs):
    """
    used to create an initial nested list from tokenized input
    raises a ValueError on mismatched parentheses
    """
    stack = [[]]
    for x in xs:
        if x == '(':
            stack[-1].append([])
            stack.append(stack[-1][-1])
        elif x == ')':
            stack.pop()
            if not stack:
                raise ValueError("Mismatched parens: too many right parentheses")
        else:
            stack[-1].append(x)
    if len(stack) > 1:
        raise ValueError("Mismatched parens: too many left parentheses")
    k = stack.pop()
    return k.pop() if len(k) == 1 else k

######################################################################################

def internalize(e):
    """
    make application and lambda abstraction explicit
    params and variables are strings
    lambda abtraction is represented by a pair (param, e)
    lambda application is represented by a list [e1,e2]
    """
    # variable/symbol case
    if type(e) == str:
        return e
    # lambda abstraction case - convert to a tuple
    if len(e) > 3 and e[2] == '.':
        return (e[1], internalize(e[3:]))
    if type(e) == tuple:
        return (e[0],internalize(e[1]))
    else:
        if "\\" in e:
            # eg. "x y \z . z t q" where the lamba is in some arbitrary position
            for (i,x) in enumerate(e):
                if x == '\\': # find the first occurrence (recursive)
                    e = e[:i] + [internalize(e[i:])]
        # we now reduce turning [x, y, z] into [[x, y], z]
        ys = [internalize(x) for x in e]
        return reduce(lambda x,y: [x] + [y], ys)

######################################################################################

def internalized_to_string(e, strip_ids=False):
    if type(e) == str:
        if strip_ids:
            s = e.split('_')
            return s[0]
        return e
    if type(e) == tuple:
        return "(\\" + internalized_to_string(e[0],strip_ids) + "." + internalized_to_string(e[1],strip_ids) + ")"
    if type(e) == list:
        return "(" + internalized_to_string(e[0],strip_ids) + " " + internalized_to_string(e[1],strip_ids) + ")"

######################################################################################

def alpha_renaming(e,dic={},depth=0):
    if type(e) == tuple:
        # we are introducing a new variable!
        # need to keep track of its scope
        eid = e[0] + "_" + str(depth)
        dic[e[0]] = eid
        return (eid, alpha_renaming(e[1],dic,depth+1))
    if type(e) == str:
        return dic.get(e,e)
    if type(e) == list:
        # still only two items in the list :)
        return map(lambda x : alpha_renaming(x,dic,depth), e)


######################################################################################

def replace_var(expr, var, term):
    if type(expr) == str:
        return term if expr == var else expr
    if type(expr) == tuple:
        if expr[0] == term:
            raise ValueError("term to replace is identical to param in lambda abstraction!")
        return (expr[0], replace_var(expr[1],var,term))
    if type(expr) == list:
        return map(lambda x: replace_var(x,var,term),expr)

def beta_reduction(e, args=[]):
    if type(e) == list:
        if type(e[0]) == str:
            args.reverse()
            args.insert(0, e)
            return reduce(lambda x,y: [x] + [y], args)
        else:
            args.append(e[1])
            return beta_reduction(e[0]) # we do not evaluate the argument! lazy.
    if type(e) == tuple:
        if not args:
            return e
        else:
            arg = args.pop()
            return beta_reduction(replace_var(e[1],e[0],arg))
    if type(e) == str:
        if args:
            arg = args.pop()
            return beta_reduction([e,arg])
        else:
            return e

######################################################################################

def identical_strings_up_to_naming(e1,e2):
    # assumes both e1 and e2 are STRINGS in normal form
    u1 = tokenize(e1)
    u2 = tokenize(e2)
    if len(u1) != len(u2):
        return False
    d = {}
    for (x,y) in zip(u1,u2):
        if x in d:
            if d[x] != y:
                return False
        else:
            d[x] = y
    return True

######################################################################################



######################################################################################

def string_to_internalized(xs,lookup=None):
    e = tokenize(xs)
    if lookup:
        kv = {}
        for x in e:
            if x in lookup:
                kv[x] = lookup[x]

        u = internalize(parens_to_lists(e))

        for (k,v) in kv.items():
            u = replace_var(u, k, v)
        # print internalized_to_string(u)
        return beta_reduction(alpha_renaming(u))
    else:
        return beta_reduction(alpha_renaming(internalize(parens_to_lists(e))))


######################################################################################

d = {}
d['I'] = string_to_internalized(r"\x.x")

if __name__ == '__main__':
    try:
        xs = sys.argv[1]
        print d['I']
        i = string_to_internalized(xs, lookup=d)
        print internalized_to_string(i, strip_ids=True)


    except IndexError:
        print "pass a lambda expression eg. \'\\x. x x x\'"
