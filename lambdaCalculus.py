#!/usr/bin/env python

import logging, sys

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

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
    # var case
    if type(e) == str:
        # logging.debug("returning token: " + e)
        return e
    # lambda abstraction case - convert to a tuple
    if len(e) > 3 and e[2] == '.':
        return (e[1], internalize(e[3:]))
    if type(e) == tuple:
        # logging.debug("internalized lambda application of " + e[0] + " to ", e[1])
        # logging.debug("passing right hand side to internalize")
        return (e[0],internalize(e[1]))
    else:
        if "\\" in e:
            # logging.debug("non parenthesised lambda application in ", e)
            # eg. "x y \z . z t q" where the lamba is in some arbitrary position
            # should be x y \z . z
            for (i,x) in enumerate(e):
                if x == '\\': # find the first occurrence (recursive)
                    # logging.debug("found occurrence of '\\' at position " + str(i))
                    lhs = e[:i]
                    rhs = e[i:]
                    new_rhs = internalize(rhs)
                    e = lhs + [new_rhs]
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

def replace_symbol(lists, old, new):
    # print "replacing variable " + old + " with " + parsed_to_string(new) + " in " + parsed_to_string(lists)
    if type(lists) != list:
        return new if lists == old else lists
    else:
        return map(lambda x: replace_symbol(x,old,new), lists)

######################################################################################

def replace_var(expr, var, term):
    # try to replace all occurences of var with term
    if type(expr) == str:
        return term if expr == var else expr
    if type(expr) == tuple:
        if expr[0] == term:
            raise ValueError("term to replace is identical to param in lambda abstraction!") # should never happen!
        return (expr[0], replace_var(expr[1],var,term))
    if type(expr) == list:
        return map(lambda x: replace_var(x,var,term),expr)

def beta_reduction(e, args=[]):
    # print ("args = ", args)
     # append and pop to/from the end of args last in first out (LIFO)
    if type(e) == list:
        # print ("application of " +  internalized_to_string(e[0]) + " to " + internalized_to_string(e[1]))
        if type(e[0]) == str:
            # print ("no further reduction possible")
            args.reverse()
            args.insert(0, e)
            return reduce(lambda x,y: [x] + [y], args)
        else:
            args.append(e[1])
            return beta_reduction(e[0]) # note that we do not evaluate the argument! are we lazy?
    if type(e) == tuple:
        if not args:
            # print ("no args to apply, returning lambda abstraction")
            return e
        else:
            arg = args.pop()
            # print ("replacing " +  internalized_to_string(e[0]) + " with " + internalized_to_string(arg) + " in " + internalized_to_string(e[1]))
            return beta_reduction(replace_var(e[1],e[0],arg)) # where e[1] is the body, e[0] is the bound lambda variable
    if type(e) == str:
        print ("get to symbol: " + e)
        if args:
            arg = args.pop()
            return beta_reduction([e,arg]) # should lead to "no further reduction possible"
        else:
            return e

######################################################################################

def parse(xs):
    return internalize(parens_to_lists(tokenize(xs)))

######################################################################################

if __name__ == '__main__':
    try:
        xs = sys.argv[1]
        e = parse(xs)
        # print(e)
        # print(internalized_to_string(e))
        a = alpha_renaming(e)
        # print(internalized_to_string(a))
        # print(internalized_to_string(a, strip_ids=True))
        b = beta_reduction(a)
        print(internalized_to_string(b, strip_ids=True))

    except IndexError:
        print "pass a lambda expression eg. \'\\x. x x x\'"
