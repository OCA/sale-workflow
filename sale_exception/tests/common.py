# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

import functools
from contextlib import contextmanager
from unittest.mock import patch


@contextmanager
def mock_detect_exception_method_env(self, env=None):
    if env is None:
        env = self.env
    with patch(
        "odoo.addons.sale_exception.models.sale_order_line.Environment"
    ) as mocked_env:
        mocked_env.return_value = env
        yield


def patch_detect_exception_method_env(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        with mock_detect_exception_method_env(self):
            return func(self, *args, **kwargs)

    return wrapper
