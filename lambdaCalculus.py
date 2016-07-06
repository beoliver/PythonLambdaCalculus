
# we will assume that we are parsing raw strings which means that we can use \ without having to escape it.

def tokenize(string):
    xs = string.replace('.',' . ').replace('(',' ( ').replace(')',' ) ').replace('\\',' \\ ')
    return xs.split()

def parens_to_nested_lists(xs):
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

def add_explicit_application_lists(xs):
    if not xs:
        return xs
    if len(xs) > 3:
        if xs[2] == '.':
            rhs = xs[3:]
            return xs[0:3] + apply_list(rhs)
    else:
        for i in range(len(xs)):
            if type(xs[i]) == list:
                xs[i] = apply_list(xs[i])
    if len(xs) == 2:
        return xs # or [xs] ?
    if len(xs) < 2:
        return xs
    base = [xs[0],xs[1]]
    for i in range(2,len(xs)):
        base = [base, xs[i]]
    return [base]

def add_explicit_lambda_lists(xs):
    if type(xs) != list:
        return xs
    if xs[0] =='\\':
        rhs = add_explicit_lambda_lists(xs[3:])
        new = [xs[:3] + rhs]
        return new[0] if len(new) == 1 else new
    else:
        return map(add_explicit_lambda_lists, xs)

def nested_lists_to_string(xs,left="(", right=")"):
    if type(xs) == list:
        return left + ' '.join(internalized_to_string(x) for x in xs) + right
    else:
        return xs


def parse(string):
    new = add_explicit_lambda_lists(add_explicit_application_brackets(parens_to_nested_lists(tokenize(string))))
    return new

def pprint_parsed(lists):
    print nested_lists_to_string(lists).replace("\\ ","\\").replace(" . ", ".")


# >>> t = parse(r'(\x. \y. \z. x y z) t')
# >>> pprint_parsed(t)
# ((\x.\y.\z.((x y) z)) t)
