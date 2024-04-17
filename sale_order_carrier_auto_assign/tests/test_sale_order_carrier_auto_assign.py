# Copyright 2020 Camptocamp SA
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import Form, TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestSaleOrderCarrierAutoAssignCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env["base"].with_context(**DISABLED_MAIL_CONTEXT).env

        cls.partner = cls.env.ref("base.res_partner_2")
        cls.product_storable = cls.env.ref("product.product_product_9")
        cls.delivery_local_delivery = cls.env.ref("delivery.delivery_local_delivery")
        cls.delivery_local_delivery.fixed_price = 10


class TestSaleOrderCarrierAutoAssignOnCreate(TestSaleOrderCarrierAutoAssignCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings = cls.env["res.config.settings"].create({})

    def test_sale_order_carrier_auto_assign_onchange(self):
        self.assertEqual(
            self.partner.property_delivery_carrier_id, self.delivery_local_delivery
        )
        self.settings.carrier_auto_assign_on_create = True
        self.settings.set_values()
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        sale_order = sale_order_form.save()
        self.assertEqual(sale_order.carrier_id, self.delivery_local_delivery)

    def test_sale_order_carrier_auto_assign_create(self):
        self.assertEqual(
            self.partner.property_delivery_carrier_id, self.delivery_local_delivery
        )
        self.settings.carrier_auto_assign_on_create = True
        self.settings.set_values()
        sale_order = self.env["sale.order"].create({"partner_id": self.partner.id})
        self.assertEqual(sale_order.carrier_id, self.delivery_local_delivery)

    def test_sale_order_carrier_auto_assign_disabled(self):
        self.assertEqual(
            self.partner.property_delivery_carrier_id, self.delivery_local_delivery
        )
        self.settings.carrier_auto_assign_on_create = False
        self.settings.set_values()
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        sale_order = sale_order_form.save()
        self.assertFalse(sale_order.carrier_id)

    def test_sale_order_carrier_auto_assign_no_carrier(self):
        self.partner.property_delivery_carrier_id = False
        self.settings.carrier_auto_assign_on_create = True
        self.settings.set_values()
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        sale_order = sale_order_form.save()
        self.assertFalse(sale_order.carrier_id)

    def test_sale_order_carrier_auto_assign_carrier_already_set(self):
        self.assertEqual(
            self.partner.property_delivery_carrier_id, self.delivery_local_delivery
        )
        self.settings.carrier_auto_assign_on_create = True
        carrier = self.env.ref("delivery.delivery_carrier")
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "carrier_id": carrier.id,
            }
        )
        self.assertEqual(sale_order.carrier_id, carrier)


class TestSaleOrderCarrierAutoAssignOnConfirm(TestSaleOrderCarrierAutoAssignCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings = cls.env["res.config.settings"].create({})
        cls.settings.carrier_auto_assign_on_confirm = True
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
        self.settings.carrier_auto_assign_on_confirm = False
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
