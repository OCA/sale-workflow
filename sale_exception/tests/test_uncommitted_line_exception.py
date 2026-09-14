# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.api import Environment
from odoo.sql_db import db_connect
from odoo.tests import TransactionCase

from odoo.addons.base_exception.tests.common import mock_base_exception_method_env


class TestSaleExceptionUncommittedLine(TransactionCase):
    """Regression test: adding a product to an already confirmed sale order
    must not crash with a ``MissingError``.

    ``base_exception.detect_exceptions()`` deliberately opens a genuinely
    independent DB connection (``self.env.registry.cursor()``) so exception
    flags survive even if the ongoing transaction later rolls back. When
    ``detect_exceptions()`` runs on a ``sale.order.line`` created earlier in
    that SAME ongoing transaction (e.g. the line just added while editing a
    confirmed order, in the same ``write()`` call that triggers the check),
    that independent connection cannot see the not-yet-committed line, and
    ``sale.order.line._get_main_records()`` (``self.mapped("order_id")``)
    used to raise ``MissingError`` when evaluated through it.

    Odoo's test machinery makes ``registry.cursor()`` return a
    savepoint-based ``TestCursor`` sharing the SAME underlying connection,
    which always sees uncommitted rows, so it can never reproduce this on
    its own. To exercise the real, production code path this test opens a
    genuinely separate connection with ``db_connect(...).cursor()`` (the
    same technique Odoo core uses in its own
    ``odoo/addons/base/tests/test_db_cursor.py``) and substitutes it via
    ``mock_base_exception_method_env``.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Force detect_exceptions() to actually build an Environment() call
        # (bypassing the test_enable short-circuit), so our mocked
        # Environment below is the one used as new_env.
        cls.env = cls.env(context=dict(cls.env.context, test_base_exception=True))
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.product_1 = cls.env.ref("product.product_product_6")
        cls.product_2 = cls.env.ref("product.product_product_7")

    def test_add_line_to_confirmed_order_uncommitted(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product_1.id, "product_uom_qty": 1}
                    )
                ],
            }
        )
        order.action_confirm()
        self.assertEqual(order.state, "sale")

        real_cr = db_connect(self.env.cr.dbname).cursor()
        self.addCleanup(real_cr.close)
        real_env = Environment(real_cr, self.env.uid, self.env.context)
        with mock_base_exception_method_env(self, env=real_env):
            # Must not raise MissingError: the new line only exists in this
            # (not yet committed) transaction, and detect_exceptions() is
            # forced above to check it through the genuinely separate
            # real_cr connection, just like a real (non-test) request would.
            order.write(
                {
                    "order_line": [
                        Command.create(
                            {
                                "product_id": self.product_2.id,
                                "product_uom_qty": 1,
                            }
                        )
                    ]
                }
            )
        self.assertEqual(len(order.order_line), 2)
