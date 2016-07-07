#!/usr/bin/env python
import sys
from lambdaCalculus import string_to_internalized, internalized_to_string
import readline

import cmd


glob_dict = {}

class LambdaEvaluator(cmd.Cmd):
    """Simple command processor example."""

    prompt = 'prompt: '
    intro = "A shitty REPL that doesn't work! HAVE FUN"

    def default(self, line):
        i = string_to_internalized(line,lookup=glob_dict)
        print internalized_to_string(i, strip_ids=True)

    def do_let(self, line):
        xs = line.split()
        if xs[1] != '=':
            print "let <var> = <expr>"
        else:
            ys = ''.join(xs[2:])
            print ys
            t = string_to_internalized(ys, lookup=glob_dict)
            glob_dict[xs[0]] = internalized_to_string(t, strip_ids=True)

    def do_EOF(self, line):
        return True

if __name__ == '__main__':
    LambdaEvaluator().cmdloop()
