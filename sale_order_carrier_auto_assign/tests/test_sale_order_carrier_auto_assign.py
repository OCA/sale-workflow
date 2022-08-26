# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import Form, TransactionCase


class TestSaleOrderCarrierAutoAssign(TransactionCase):
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

    def test_sale_order_carrier_auto_assign(self):
        self.assertEqual(
            self.partner.property_delivery_carrier_id, self.normal_delivery_carrier
        )
        self.assertFalse(self.sale_order.carrier_id)
        self.sale_order.action_confirm()
        self.assertEqual(self.sale_order.state, "sale")
        self.assertEqual(self.sale_order.carrier_id, self.normal_delivery_carrier)
        delivery_line = self.sale_order.order_line.filtered(lambda l: l.is_delivery)
        delivery_rate = self.normal_delivery_carrier.rate_shipment(self.sale_order)
        self.assertEqual(delivery_line.price_unit, delivery_rate["carrier_price"])

    def test_sale_order_carrier_auto_assign_no_carrier(self):
        self.partner.property_delivery_carrier_id = False
        self.assertFalse(self.sale_order.carrier_id)
        self.sale_order.action_confirm()
        self.assertEqual(self.sale_order.state, "sale")
        self.assertFalse(self.sale_order.carrier_id)
