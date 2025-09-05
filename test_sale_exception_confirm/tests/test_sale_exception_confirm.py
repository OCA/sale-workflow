# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.fields import Command
from odoo.tests import TransactionCase


class TestSaleExceptionConfirm(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.no_free_exception = cls.env.ref("sale_exception.excep_no_free")
        # cls.no_free_exception.active = True
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.product = cls.env.ref("product.product_product_9")

    def test_action_confirm_rollback(self):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "product_uom_qty": 1.0,
                            "price_unit": 0.0,
                        },
                    )
                ],
            }
        )
        self.assertFalse(sale_order.before_confirm)
        self.assertFalse(sale_order.after_confirm)
        self.assertTrue(self.no_free_exception.active)
        sale_order.action_confirm()
        self.assertEqual(sale_order.exception_ids, self.no_free_exception)
        self.assertEqual(sale_order.state, "draft")
        self.assertFalse(sale_order.before_confirm)
        self.assertFalse(sale_order.after_confirm)
