# Copyright 2024 Tecnativa - Sergio Teruel

from odoo.tests import Form, TransactionCase


class TestSaleCancelWizardOptional(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "test cancel", "list_price": 1000}
        )
        cls.partner = cls.env["res.partner"].create({"name": "test - partner"})
        cls.order = cls._create_sale_order(cls, [(cls.product, 10)])

    def _create_sale_order(self, products_info):
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.partner
        for product, qty in products_info:
            with order_form.order_line.new() as line_form:
                line_form.product_id = product
                line_form.product_uom_qty = qty
        return order_form.save()

    def test_cancel_with_wizard(self):
        self.order.with_context(
            tracking_disable=True, test_sale_order_cancel_wizard_optional=True
        ).write({"state": "sent"})
        action = self.order.action_cancel()
        self.assertEqual(action["type"], "ir.actions.act_window")

    def test_cancel_without_wizard(self):
        self.order.with_context(
            tracking_disable=True, test_sale_order_cancel_wizard_optional=True
        ).write({"state": "sent"})
        self.assertTrue(self.order.action_cancel())
