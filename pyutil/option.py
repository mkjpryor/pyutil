"""
This module contains the Option implementation

An Option represents an optional value

Options provide several methods (map, filter, etc.) to manipulate the contained
value in an empty-safe way, as well as methods to extract the contained value
in a safe (i.e. non-throwing) or unsafe (i.e. might throw) way
  
@author: Matt Pryor <mkjpryor@gmail.com>
"""

import abc


class Option(object):
    """
    Represents an optional value
    """
    
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractproperty
    def empty(self):
        """
        True if this option is empty, false otherwise
        """
        pass
    
    @abc.abstractproperty
    def value(self):
        """
        Returns the option's value
        If the option is empty, an exception will be thrown
        """
        pass

    @property
    def defined(self):
        """
        True if this option has a value, false otherwise
        """
        return not self.empty
        
    def filter(self, p):
        """
        Returns this option if it is non-empty and the predicate returns true for its value
        """
        if not self.defined:
            return self
        else:
            return self if p(self.value) else Nothing()
    
    def flat_map(self, f):
        """
        Returns the result of applying f to the value of this option if it is non-empty
        """
        return f(self.value) if self.defined else self        
    
    def flatten(self):
        """
        Transforms a nested option (of any depth) into a non-nested option
        """
        return self.value.flatten() if self.defined and isinstance(self.value, Option) else self
    
    def get_or_default(self, default):
        """
        Returns this option's value if it is non-empty, default otherwise
        """
        return self.value if self.defined else default
    
    def get_or_else(self, f):
        """
        Returns this option's value if it is non-empty, otherwise the result of evaluating f
        
        This is useful if the default value is expensive to compute
        """
        return self.value if self.defined else f()
    
    def map(self, f):
        """
        Returns a new option containing the result of applying f to this option's value
        if it is non-empty
        """
        return Just(f(self.value)) if self.defined else self
    
    def or_else(self, opt):
        """
        Returns this option if it is non-empty, otherwise opt
        """
        return self if self.defined else opt
    
    def __iter__(self):
        """
        Returns an iterator for this option
        """
        if self.defined:
            yield self.value


class Just(Option):
    """
    Represents a value that exists
    """
    
    def __init__(self, value):
        self.__value = value
        
    @property
    def empty(self):
        return False
    
    @property
    def value(self):
        return self.__value


class Nothing(Option):
    """
    Represents a value that doesn't exist
    """
    
    @property
    def empty(self):
        return True
    
    @property
    def value(self):
        raise ValueError('Cannot get value from Nothing')
