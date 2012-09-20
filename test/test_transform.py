#!/usr/bin/env python

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import astor

def TestMe(x, y, width=10, foo=None):
    from foo.bar.baz.murgatroyd import sally as bob

    a.b = c.d + x.y.z.a.b
    m.n = q = (w.w, x.x.y.y) = f(x.x.y.z)

func_ast = astor.codetoast(TestMe)
print(astor.dump(func_ast))
print(astor.to_source(func_ast))

class ConsolidateAttributes(astor.TreeWalk):
    def post_Attribute(self):
        node = self.cur_node
        value = node.value
        value.id += '.' + node.attr
        self.replace(value)

ConsolidateAttributes(func_ast)

class FindNames(astor.TreeWalk):
    def init_Assign(self):
        self.assignments = []
        self.current_assign = None
    def pre_Assign(self):
        self.current_assign = [], []
    def post_Assign(self):
        self.assignments.append(self.current_assign)
        self.current_assign = None

    def pre_targets_name(self):
        self.in_targets = True
    def post_targets_name(self):
        self.in_targets = False
    def post_Name(self):
        if self.current_assign:
            self.current_assign[self.in_targets].append(self.cur_node.id)

x = FindNames(func_ast)
print(x.assignments)


print('')
print('')
print(astor.dump(func_ast))
print(astor.to_source(func_ast))
