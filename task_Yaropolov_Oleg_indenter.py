from contextlib import ContextDecorator

class Indenter(ContextDecorator):
    """Indenter realization"""
    def __init__(self, indent_str=" " * 4, indent_level=0):
        self.indent_str = indent_str
        self.indent_level = indent_level

    def __enter__(self):
        self.indent_level += 1
        return self

    def __exit__(self, *exc):
        self.indent_level -= 1
        return self

    def print(self, args):
        """modification of print"""
        print(self.indent_str * (self.indent_level - 1) + args)
