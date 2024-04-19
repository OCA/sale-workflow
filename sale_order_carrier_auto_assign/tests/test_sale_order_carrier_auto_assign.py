# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import Form, TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


# Common class for OnCreate and OnConfirm
class TestSaleOrderCarrierAutoAssignCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env["base"].with_context(**DISABLED_MAIL_CONTEXT).env

        cls.partner = cls.env.ref("base.res_partner_2")
        cls.product_storable = cls.env.ref("product.product_product_9")
        cls.product_service = cls.env.ref("product.expense_product")
        cls.delivery_local_delivery = cls.env.ref("delivery.delivery_local_delivery")
        cls.delivery_local_delivery.fixed_price = 10


class TestSaleOrderCarrierAutoAssignOnConfirm(TestSaleOrderCarrierAutoAssignCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings = cls.env["res.config.settings"].create({})
        cls.settings.carrier_auto_assign = True
        cls.settings.set_values()
        cls.sale_order_form = Form(cls.env["sale.order"])
        cls.sale_order_form.partner_id = cls.partner
        with cls.sale_order_form.order_line.new() as line_form:
            line_form.product_id = cls.product_storable
        cls.sale_order = cls.sale_order_form.save()

    def test_sale_order_carrier_auto_assign(self):
        self.assertEqual(
            self.partner.property_delivery_carrier_id, self.delivery_local_delivery
        )
        self.assertFalse(self.sale_order.carrier_id)
        self.sale_order.action_confirm()
        self.assertEqual(self.sale_order.state, "sale")
        self.assertEqual(self.sale_order.carrier_id, self.delivery_local_delivery)
        delivery_line = self.sale_order.order_line.filtered(lambda l: l.is_delivery)
        delivery_rate = self.delivery_local_delivery.rate_shipment(self.sale_order)
        self.assertEqual(delivery_line.price_unit, delivery_rate["carrier_price"])

    def test_sale_order_carrier_auto_assign_disabled(self):
        self.assertEqual(
            self.partner.property_delivery_carrier_id, self.delivery_local_delivery
        )
        self.assertFalse(self.sale_order.carrier_id)
        self.settings.carrier_auto_assign = False
        self.settings.set_values()
        self.sale_order.action_confirm()
        self.assertEqual(self.sale_order.state, "sale")
        self.assertFalse(self.sale_order.carrier_id)

    def test_sale_order_carrier_auto_assign_no_carrier(self):
        self.partner.property_delivery_carrier_id = False
        self.assertFalse(self.sale_order.carrier_id)
        self.sale_order.action_confirm()
        self.assertEqual(self.sale_order.state, "sale")
        self.assertFalse(self.sale_order.carrier_id)

    def test_sale_order_carrier_auto_assign_carrier_already_set(self):
        self.assertEqual(
            self.partner.property_delivery_carrier_id, self.delivery_local_delivery
        )
        carrier = self.env.ref("delivery.delivery_carrier")
        self.sale_order.carrier_id = carrier
        self.sale_order.action_confirm()
        self.assertEqual(self.sale_order.state, "sale")
        self.assertEqual(self.sale_order.carrier_id, carrier)

    def test_sale_order_carrier_auto_assign_all_service(self):
        self.assertEqual(
            self.partner.property_delivery_carrier_id, self.delivery_local_delivery
        )
        self.sale_order.order_line.product_id = self.product_service
        self.sale_order.action_confirm()
        self.assertEqual(self.sale_order.state, "sale")
        self.assertFalse(self.sale_order.carrier_id)
