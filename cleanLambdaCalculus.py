#!/usr/bin/env python
import sys

########################################################################################
########################################################################################
########################################################################################

def tokenize(input_string):
    # convert a string literal (eg. r"(\x. x x) y") into a list of tokens
    # ["(", "\\", "x", ".", "x", "x", ")", "y", ")"]
    # no real need to use regex as we only have 4 special characters!
    replacements = ('.',' . '), ('(',' ( '), (')',' ) '), ('\\',' \\ ')
    return reduce(lambda a, kv: a.replace(*kv), replacements, input_string).split()

def parens_to_lists(xs):
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

def internalize_recursive(e):
    if type(e) == str:
        return e
    if len(e) > 3 and e[2] == '.':
        return (e[1], internalize_recursive(e[3:]))
    if type(e) == tuple:
        return (e[0],internalize_recursive(e[1]))
    else:
        if "\\" in e:
            for (i,x) in enumerate(e):
                if x == '\\':
                    if i == 0:
                        raise ValueError("Can not parse expression")
                    e = e[:i] + [internalize_recursive(e[i:])]
        ys = [internalize_recursive(x) for x in e]
        return reduce(lambda x,y: [x] + [y], ys)


########################################################################################

def internalize(string):
    return internalize_recursive(parens_to_lists(tokenize(string)))

########################################################################################

def internal_to_string(e, ids=False):
    if type(e) == str:
        return e.split('_')[0] if not ids else e
    if type(e) == tuple:
        left, mid, right = '(\\', '.', ')'
    if type(e) == list:
        left, mid, right = '(', ' ', ')'
    return left + mid.join(map(lambda x: internal_to_string(x,ids), e)) + right

########################################################################################

def replace_var(e, var, term):
    if type(e) == str:
        return term if e == var else e
    if type(e) == tuple:
        if e[0] == term:
            raise ValueError("term to replace is identical to param in lambda abstraction!")
        return (e[0], replace_var(e[1],var,term))
    if type(e) == list:
        return map(lambda x: replace_var(x,var,term),e)

########################################################################################

def alpha_conversion(e):
    def alpha_conversion_r(e, mappings, depth):
        if type(e) == tuple:
            eid = e[0] + "_" + str(depth)
            mappings[e[0]] = eid
            return (eid, alpha_conversion_r(e[1], mappings, depth+1))
        if type(e) == str:
            return mappings.get(e,e)
        if type(e) == list:
            return map(lambda x : alpha_conversion_r(x,mappings,depth), e)
    return alpha_conversion_r(e, {}, 0)

########################################################################################

def beta_reduction(e):
    def beta_reduction_r(e, args):
        if type(e) == list:
            if type(e[0]) == str:
                args.reverse()
                args.insert(0, e)
                return reduce(lambda x,y: [x] + [y], args)
            else:
                args.append(e[1])
                return beta_reduction_r(e[0],args)
        if type(e) == tuple:
            if not args:
                return e
            else:
                arg = args.pop()
                return beta_reduction_r(replace_var(e[1],e[0],arg),args)
        if type(e) == str:
            if args:
                arg = args.pop()
                return beta_reduction_r([e,arg],args)
            else:
                return e
    return beta_reduction_r(e, [])

########################################################################################


class LambdaExpression(object):
    """
    a simple wrapper for lambda expressions. Allows us to keep multiple
    representations at the same time etc.
    """
    def __init__(self,s):
        self.internal = beta_reduction(alpha_conversion(internalize(s)))
    def toString(self):
        return internal_to_string(self.internal,ids=False) if self.internal else ''


if __name__ == '__main__':

    try:
        string = sys.argv[1]

        e = LambdaExpression(string)
        print e.toString()

    except IndexError:
        print "pass a lambda expression eg. \'\\x. x x x\'"
