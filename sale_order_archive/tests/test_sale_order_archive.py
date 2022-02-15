# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.exceptions import UserError
from odoo.tests import Form, TransactionCase


class TestSaleOrderArchive(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        test_context = cls.env.context.copy()
        test_context["test_carrier_auto_assign"] = True
        cls.env = cls.env(context=dict(test_context, tracking_disable=True))
        cls.partner = cls.env.ref("base.res_partner_2")
        product = cls.env.ref("product.product_product_9")
        cls.normal_delivery_carrier = cls.env.ref("delivery.normal_delivery_carrier")
        cls.normal_delivery_carrier.fixed_price = 10
        sale_order_form = Form(cls.env["sale.order"])
        sale_order_form.partner_id = cls.partner
        with sale_order_form.order_line.new() as line_form:
            line_form.product_id = product
        cls.sale_order = sale_order_form.save()

    def test_sale_order_archive_toggle_active(self):
        self.assertTrue(self.sale_order.active)
        self.sale_order.state = "done"
        self.sale_order.toggle_active()
        self.assertFalse(self.sale_order.active)

    def test_sale_order_archive_donot_toggle_active(self):
        self.assertTrue(self.sale_order.active)
        regex = r"Only 'Locked' or 'Canceled' orders can be archived"
        with self.assertRaisesRegex(UserError, regex):
            self.sale_order.toggle_active()
        self.assertTrue(self.sale_order.active)
