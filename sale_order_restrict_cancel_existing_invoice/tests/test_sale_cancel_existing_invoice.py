# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestSaleOrderCancelExistingInvoice(TransactionCase):
    def setUp(self):
        super().setUp()

        self.product = self.env.ref("product.product_product_4")
        self.partner = self.env.ref("base.res_partner_1")
        self.advance_obj = self.env["sale.advance.payment.inv"]

    def _create_sale(self):
        line = [
            (
                0,
                0,
                {
                    "product_id": self.product.id,
                    "product_uom": self.product.uom_id.id,
                    "product_uom_qty": 3.0,
                },
            )
        ]
        vals = {
            "partner_id": self.partner.id,
            "order_line": line,
        }
        self.sale = self.env["sale.order"].create(vals)

    def _create_invoice_advance(self):
        vals = {
            "advance_payment_method": "percentage",
            "amount": 10.0,
        }
        self.advance = self.advance_obj.create(vals)

    def test_cancel(self):
        self._create_sale()
        self._create_invoice_advance()

        self.advance.with_context(active_ids=[self.sale.id]).create_invoices()
        self.sale.invoice_ids.action_post()

        with self.assertRaises(UserError):
            self.sale.action_cancel()
