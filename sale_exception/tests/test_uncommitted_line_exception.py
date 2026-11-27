# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests import TransactionCase

from odoo.addons.base_exception.exceptions import BaseExceptionError


class TestSaleExceptionUncommittedLine(TransactionCase):
    """Regression test: confirming an order whose lines were created in the
    same transaction must raise the exception, not a ``MissingError``.

    ``base_exception.detect_exceptions()`` deliberately opens a genuinely
    independent DB connection (``self.env.registry.cursor()``) so exception
    flags survive even if the ongoing transaction later rolls back. That
    connection cannot see the records created by the ongoing transaction,
    which used to raise ``MissingError`` when writing their exceptions
    through it.

    The registry is not in test mode here, so ``registry.cursor()`` returns
    a genuinely separate connection, as in a real (non-test) request.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Bypass the test_enable short-circuit of detect_exceptions(), so the
        # second cursor is used.
        cls.env = cls.env(context=dict(cls.env.context, test_base_exception=True))
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.product = cls.env.ref("product.product_product_6")
        cls.rule = cls.env["exception.rule"].create(
            {
                "name": "Big quantity",
                "model": "sale.order.line",
                "exception_type": "by_domain",
                "domain": "[('product_uom_qty', '>', 5)]",
            }
        )

    def _create_order(self, qty):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product.id, "product_uom_qty": qty}
                    )
                ],
            }
        )

    def test_confirm_order_uncommitted_lines(self):
        order = self._create_order(10)
        with self.assertRaises(BaseExceptionError):
            order.action_confirm()

    def test_confirm_order_uncommitted_lines_no_exception(self):
        order = self._create_order(1)
        order.action_confirm()
        self.assertEqual(order.state, "sale")
