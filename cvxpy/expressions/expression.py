"""
Copyright 2013 Steven Diamond

This file is part of CVXPY.

CVXPY is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

CVXPY is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CVXPY.  If not, see <http://www.gnu.org/licenses/>.
"""


from .. import settings as s
from .. import utilities as u
from .. import interface as intf
from ..constraints import leq_constraint as le
from ..constraints import eq_constraint as eq
import types
import abc

class Expression(u.Canonicalizable):
    """
    A mathematical expression in a convex optimization problem.
    """
    __metaclass__ = abc.ABCMeta
    # # Returns the value of the expression.
    # TODO make this recursive
    # @property
    # def value(self):
    #     return self.objective.value(intf.DEFAULT_INTERFACE)

    # TODO priority
    def __repr__(self):
        return self.name()

    # Returns string representation of the expression.
    @abc.abstractmethod
    def name(self):
        return NotImplemented

    # The curvature of the expression.
    @property
    def curvature(self):
        return self._context.curvature

    # The sign of the expression, a (row,col) tuple.
    @property
    def sign(self):
        return self._context.sign

    # The shape of the expression, an object.
    @property
    def shape(self):
        return self._context.shape

    # The dimensions of the expression.
    @property
    def size(self):
        return self._context.shape.size

    # Is the expression a scalar?
    def is_scalar(self):
        return self.size == (1,1)

    # Is the expression a column vector?
    def is_vector(self):
        return self.size[1] == 1

    # Cast to Constant if not an Expression.
    @staticmethod
    def cast_to_const(expr):
        return expr if isinstance(expr, Expression) else types.constant()(expr)

    """ Iteration """
    # Create a new variable that acts as a view into this variable.
    # Updating the variable's value updates the value of this variable instead.
    def __getitem__(self, key):
        key = u.Key.validate_key(key, self)
        # Indexing into a scalar returns the scalar.
        if self.size == (1,1):
            return self
        else:
            return self.index_object(key)
        # TODO # Set value if variable has value.
        # if self.value is not None:
        #     index_var.primal_value = self.value[key]

    # Iterating over the leaf returns the index expressions
    # in column major order.
    def __iter__(self):
        for col in range(self.size[1]):
            for row in range(self.size[0]):
                yield self[row,col]

    def __len__(self):
        length = self.size[0]*self.size[1]
        if length == 1: # Numpy will iterate over anything with a length.
            return NotImplemented
        else:
            return length

    """ Arithmetic operators """
    def __add__(self, other):
        return types.add_expr()(self, other)

    # Called for Number + Expression.
    def __radd__(self, other):
        return Expression.cast_to_const(other) + self

    def __sub__(self, other):
        return types.sub_expr()(self, other)

    # Called for Number - Expression.
    def __rsub__(self, other):
        return Expression.cast_to_const(other) - self

    def __mul__(self, other):
        return types.mul_expr()(self, other)

    # Called for Number * Expression.
    def __rmul__(self, other):
        return Expression.cast_to_const(other) * self

    def __neg__(self):
        return types.neg_expr()(self)

    """ Comparison operators """
    def __eq__(self, other):
        return eq.EqConstraint(self, other)

    def __le__(self, other):
        return le.LeqConstraint(self, other)

    def __ge__(self, other):
        return Expression.cast_to_const(other).__le__(self)