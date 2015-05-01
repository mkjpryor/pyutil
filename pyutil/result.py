"""
This module contains the Result implementation

A Result represents a the result of a computation that either returned successfully
or resulted in an exception

Results provide several methods (map, filter, etc.) to manipulate the contained
value in a fail-safe way, as well as methods to extract the contained value
in a safe (i.e. non-throwing) or unsafe (i.e. might throw) way
  
@author: Matt Pryor <mkjpryor@gmail.com>
"""

import abc

from pyutil import option


class Result(object):
    """
    A result represents the result of a (potentially failed) computation
    """
    
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractproperty
    def failed(self):
        """
        True if this result is a failure, False otherwise
        """
        pass
    
    @abc.abstractproperty
    def error(self):
        """
        If this result is a failure, this is the exception that caused it
        If this result is a success, an exception is thrown
        """
        pass
    
    @abc.abstractproperty
    def result(self):
        """
        If this result is a success, this is the result
        If this result is a failure, the exception that caused it is thrown
        """
        pass
    
    @property
    def success(self):
        """
        True if this result is a success, False otherwise
        """
        return not self.failed
        
    def filter(self, p):
        """
        Returns this result if it is a success and the predicate returns true for its result
        """
        return self if self.success and p(self.result) else Failure(ValueError('Predicate failed'))
    
    def flat_map(self, f):
        """
        Returns the result of applying f to the result of this result if it is a success
        """
        return f(self.result) if self.success else self       
    
    def flatten(self):
        """
        Transforms a nested Result into a non-nested Result
        """
        return self.result.flatten() if self.success and isinstance(self.result, Result) else self
    
    def get_or_default(self, default):
        """
        Returns this result's result if it is a success, default otherwise
        """
        return self.result if self.success else default
    
    def get_or_else(self, f):
        """
        Returns this result's result if it is a success, otherwise the result of evaluating f
        
        This is useful if the default value is expensive to compute
        """
        return self.result if self.success else f()
    
    def map(self, f):
        """
        Returns a new result containing the result of applying f to this result's result
        if it is a success
        """
        return Success(f(self.result)) if self.success else self
    
    def or_else(self, opt):
        """
        Returns this result if it is a success, otherwise opt
        """
        return self if self.success else opt
    
    def recover(self, f):
        """
        Returns a new result containing the result of applying f to this result's error if it is a failure
        """
        return Success(f(self.error)) if self.failed else self
    
    def to_option(self):
        """
        Converts this result to an option
        
        Successes are converted to just and failures are converted to nothing
        """
        return option.Just(self.result) if self.success else option.Nothing()
    
    def __iter__(self):
        """
        Returns an iterator for this result
        """
        if self.success:
            yield self.result


class Success(Result):
    """
    Represents the result of a successful computation
    """
    
    def __init__(self, result):
        self.__result = result
    
    @property
    def failed(self):
        return False
    
    @property
    def error(self):
        raise TypeError('Cannot retrieve error from a Success')
    
    @property
    def result(self):
        return self.__result


def Failure(Result):
    """
    Represents the result of a failed computation
    """
    
    def __init__(self, error):
        if not isinstance(error, Exception):
            raise TypeError('Failure must be created with an Exception')
        self.__error = error
    
    @property
    def failed(self):
        return True
    
    @property
    def error(self):
        return self.__error
    
    @property
    def result(self):
        raise self.__error
