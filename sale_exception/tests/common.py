# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
try:
    from decorator import decoratorx as decorator
except ImportError:
    from decorator import decorator

from contextlib import contextmanager
from unittest.mock import patch

from odoo.addons.base_exception.exceptions import BaseExceptionError


@contextmanager
def mock_detect_exception_method_env(self, env=None):
    if env is None:
        env = self.env
    with patch(
        "odoo.addons.sale_exception.models.sale_order_line.Environment"
    ) as mocked_env:
        mocked_env.return_value = env
        yield


@decorator
def patch_detect_exception_method_env(func, self):
    with mock_detect_exception_method_env(self):
        return func(self)


@contextmanager
def assert_base_exception_error(test_case):
    """Assert the block raises BaseExceptionError, keeping what it stored.

    `TransactionCase.assertRaises` rolls back the savepoint it opens, which
    would also discard the exceptions the detection has just written.
    """
    try:
        yield
    except BaseExceptionError:
        return
    test_case.fail("BaseExceptionError was not raised")
