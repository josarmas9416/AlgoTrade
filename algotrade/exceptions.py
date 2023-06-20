"""The Odoo Exceptions module defines a few core exception types.

Those types are understood by the RPC layer.
Any other exception type bubbling until the RPC layer will be
treated as a 'Server error'.

.. note::
    If you consider introducing new exceptions,
    check out the :mod:`odoo.addons.test_exceptions` module.
"""

class UserError(Exception):
    """Generic error managed by the client.

    Typically when the user tries to do something that has no sense given the current
    state of a record. Semantically comparable to the generic 400 HTTP status codes.
    """

    def __init__(self, message):
        """
        :param message: exception message and frontend modal content
        """
        super().__init__(message)


class AccessDenied(UserError):
    """Login/password error.

    .. note::

        No traceback.

    .. admonition:: Example

        When you try to log with a wrong password.
    """

    def __init__(self, message="Access Denied"):
        super().__init__(message)
        self.with_traceback(None)
        self.__cause__ = None
        self.traceback = ('', '', '')


class AccessError(UserError):
    """Access rights error.

    .. admonition:: Example

        When you try to read a record that you are not allowed to.
    """


class ValidationError(UserError):
    """Violation of python constraints.

    .. admonition:: Example

        When you try to create a new user with a login which already exist in the db.
    """


class OrderError(UserError):
    """Send order error.

    .. note::

        No traceback.

    .. admonition:: Example

        When you try to send an order with wrong parameters.
    """

    def __init__(self, message):
        super().__init__(message)
        self.with_traceback(None)
        self.__cause__ = None
        self.traceback = ('', '', '')


class GeneralError(UserError):
    """General error.

    .. note::

        No traceback.

    .. admonition:: Example

        When you try to access a not implemented method.
    """

    def __init__(self, message):
        super().__init__(message)
        self.with_traceback(None)
        self.__cause__ = None
        self.traceback = ('', '', '')