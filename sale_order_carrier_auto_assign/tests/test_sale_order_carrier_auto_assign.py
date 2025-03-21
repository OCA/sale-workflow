# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderCarrierAutoAssign(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings = cls.env["res.config.settings"].create({})
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.product = cls.env.ref("product.product_product_9")
        cls.delivery_local_delivery = cls.env.ref("delivery.delivery_local_delivery")
        cls.delivery_local_delivery.fixed_price = 10
        cls.delivery_local_delivery.free_over = False

    @classmethod
    def _create_sale_order(cls):
        sale_order_form = Form(cls.env["sale.order"])
        sale_order_form.partner_id = cls.partner
        with sale_order_form.order_line.new() as line_form:
            line_form.product_id = cls.product
        return sale_order_form.save()

    def test_partner_property_delivery_carrier_id(self):
        self.assertEqual(
            self.partner.property_delivery_carrier_id, self.delivery_local_delivery
        )

    def test_sale_order_carrier_auto_assign(self):
        self.settings.carrier_auto_assign = True
        self.settings.set_values()
        sale_order = self._create_sale_order()
        self.assertFalse(sale_order.carrier_id)
        sale_order.action_confirm()
        self.assertEqual(sale_order.state, "sale")
        self.assertEqual(sale_order.carrier_id, self.delivery_local_delivery)
        delivery_line = sale_order.order_line.filtered(lambda line: line.is_delivery)
        delivery_rate = self.delivery_local_delivery.rate_shipment(sale_order)
        self.assertEqual(delivery_line.price_unit, delivery_rate["carrier_price"])

    def test_sale_order_carrier_auto_assign_no_carrier(self):
        self.settings.carrier_auto_assign = True
        self.settings.carrier_on_create = True
        self.settings.set_values()
        self.partner.property_delivery_carrier_id = False
        sale_order = self._create_sale_order()
        self.assertFalse(sale_order.carrier_id)
        sale_order.action_confirm()
        self.assertEqual(sale_order.state, "sale")
        self.assertFalse(sale_order.carrier_id)

    def test_sale_order_carrier_auto_assign_onchange(self):
        self.settings.carrier_on_create = True
        self.settings.set_values()
        sale_order = self._create_sale_order()
        self.assertEqual(sale_order.carrier_id, self.delivery_local_delivery)

    def test_sale_order_carrier_auto_assign_create(self):
        self.settings.carrier_on_create = True
        self.settings.set_values()
        sale_order = self.env["sale.order"].create({"partner_id": self.partner.id})
        self.assertEqual(sale_order.carrier_id, self.delivery_local_delivery)

    def test_sale_order_carrier_auto_assign_disabled(self):
        self.settings.carrier_on_create = False
        self.settings.set_values()
        sale_order = self._create_sale_order()
        self.assertFalse(sale_order.carrier_id)

    def test_sale_order_carrier_auto_assign_carrier_already_set(self):
        self.settings.carrier_on_create = True
        self.settings.set_values()
        carrier = self.env.ref("delivery.delivery_carrier")
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "carrier_id": carrier.id,
            }
        )
        self.assertEqual(sale_order.carrier_id, carrier)
