#!/usr/bin/env python
import sys
from cleanLambdaCalculus import LambdaExpression
import readline
import cmd

########################################################################################
########################################################################################
# TO DO
# FIX VARIABLE RENAMING... THERE ARE STILL PROBLEMS WIH SHADOWING
# after defining cons, car and cdr   car (cdr (cons 1 (cons 2 nil))) does not return 2
# if we define cons,car,cdr,cons2 with unique names it does
# i'm assuming the problem is in the call of (cons 1 (cons 2 nil))
# as it works with uniquely defined cons1 and cons2
# this is problem with cleanLambda.py, but we need to be aware of it as it means
# we are NOT getting fully correct results
########################################################################################
########################################################################################


header1 = """
    \\\\      |
     \\\\     |
    //\\\\    |
   //  \\\\   |
  //    \\\\  |
"""

#########################################################################
variableSeed = 0
glob_dict = {}
#########################################################################

class LambdaEvaluator(cmd.Cmd):
    """Simple command processor example."""

    prompt = 'prompt: '
    intro = header1

    def default(self, line):
        global variableSeed
        try:
            e = LambdaExpression(line, id_prefix=str(variableSeed), lookup=glob_dict)
        except ValueError as e:
            print e
            return
        variableSeed += 1
        # print e.beta
        print e.toString(ids=False)

    def do_let(self, line):
        global variableSeed
        if not line:
            print "let <var> = <expr>"
            return
        xs = line.split()
        if xs[1] != '=':
            print "let <var> = <expr>"
            return
        else:
            ys = ' '.join(xs[2:])
            try:
                e = LambdaExpression(ys, id_prefix=str(variableSeed), lookup=glob_dict)
            except ValueError as e:
                print e
                return
            variableSeed += 1
            # print e.beta
            print e.toString(ids=False)
            glob_dict[xs[0]] = e.beta
            return

    def do_EOF(self, line):
        return True


if __name__ == '__main__':
    LambdaEvaluator().cmdloop()
