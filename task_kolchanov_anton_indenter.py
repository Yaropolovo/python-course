'''
task #8 decorators part 2 indenter
'''
from __future__ import annotations
from contextlib import ContextDecorator


class Indenter(ContextDecorator):
    '''Indenter context decorator'''
    def __init__(self, indent_str=' '*4, indent_lvl=0):
        self.indent_str = indent_str
        self.indent_lvl = indent_lvl
        self.prefix = self.indent_str*self.indent_lvl
        def iterator_func(sign=1):
            count = -1
            def inner(sign=sign):
                nonlocal count
                count += sign*1
                return count
            return inner
        self.counter = iterator_func()


    def __enter__(self):
        self.prefix = self.indent_str*self.indent_lvl + self.indent_str*self.counter()
        return self


    def __exit__(self, *exc):
        self.prefix = self.indent_str*self.indent_lvl + self.indent_str*self.counter(-1)
        return self


    def print(self, *args):
        '''prints text with prefix'''
        print(self.prefix, end='')
        print(*args)
        #print(id(self))
