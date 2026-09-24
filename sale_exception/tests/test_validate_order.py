# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import Command, fields
from odoo.tests import TransactionCase


class TestSaleExceptionValidateOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.exception = cls.env.ref("sale_exception.excep_no_zip")
        cls.exception.active = True
        cls.partner = cls.env["res.partner"].create({"name": "No zip"})
        cls.product = cls.env.ref("product.product_product_6")
        cls.order = cls._create_order(cls.partner)

    @classmethod
    def _create_order(cls, partner):
        return cls.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    Command.create({"product_id": cls.product.id, "product_uom_qty": 1})
                ],
            }
        )

    def _sign(self, orders):
        orders.write({"signed_by": "Customer", "signed_on": fields.Datetime.now()})
        self.env.cr.flush()

    def _notes(self, order):
        return order.message_ids.filtered(
            lambda m: m.subtype_id == self.env.ref("mail.mt_note")
            and self.exception.name in m.body
        )

    def test_validate_order_with_exception(self):
        self._sign(self.order)
        self.order._validate_order()
        self.assertEqual(self.order.state, "draft")
        self.assertIn(self.exception, self.order.exception_ids)
        self.assertEqual(self.order.signed_by, "Customer")
        self.assertTrue(self._notes(self.order))

    def test_validate_order_without_exception(self):
        self.partner.zip = "1000"
        self._sign(self.order)
        self.order._validate_order()
        self.assertEqual(self.order.state, "sale")
        self.assertFalse(self.order.exception_ids)
        self.assertFalse(self._notes(self.order))

    def test_validate_order_batch(self):
        order_ok = self._create_order(
            self.env["res.partner"].create({"name": "Zip", "zip": "1000"})
        )
        orders = self.order | order_ok
        self._sign(orders)
        orders._validate_order()
        self.assertEqual(self.order.state, "draft")
        self.assertTrue(self._notes(self.order))
        self.assertEqual(order_ok.state, "sale")
        self.assertFalse(self._notes(order_ok))
