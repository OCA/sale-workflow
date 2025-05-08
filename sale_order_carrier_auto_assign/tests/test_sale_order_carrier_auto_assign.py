# Copyright 2020 Camptocamp SA
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.fields import Command
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


# Common class for OnCreate and OnConfirm
class TestSaleOrderCarrierAutoAssignCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings = cls.env["res.config.settings"].create({})
        cls.product_storable = cls.env["product.product"].create(
            {
                "name": "Test product storable",
                "type": "consu",
            }
        )
        cls.product_service = cls.env["product.product"].create(
            {
                "name": "Test product service",
                "type": "service",
            }
        )
        cls.delivery_local_delivery = cls.env.ref("delivery.delivery_local_delivery")
        cls.delivery_local_delivery.fixed_price = 10
        cls.delivery_local_delivery.free_over = False
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test partner",
                "property_delivery_carrier_id": cls.delivery_local_delivery.id,
            }
        )

    @classmethod
    def _create_sale_order(cls):
        sale_order_form = Form(cls.env["sale.order"])
        sale_order_form.partner_id = cls.partner
        with sale_order_form.order_line.new() as line_form:
            line_form.product_id = cls.product_storable
        return sale_order_form.save()


class TestSaleOrderCarrierAutoAssignOnCreate(TestSaleOrderCarrierAutoAssignCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings.carrier_on_create = True
        cls.settings.set_values()

    def test_sale_order_carrier_auto_assign_no_carrier(self):
        self.partner.property_delivery_carrier_id = False
        sale_order = self._create_sale_order()
        self.assertFalse(sale_order.carrier_id)

    def test_sale_order_carrier_auto_assign_onchange(self):
        sale_order = self._create_sale_order()
        self.assertEqual(sale_order.carrier_id, self.delivery_local_delivery)

    def test_sale_order_carrier_auto_assign_create(self):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create({"product_id": self.product_storable.id})
                ],
            }
        )
        self.assertEqual(sale_order.carrier_id, self.delivery_local_delivery)

    def test_sale_order_carrier_auto_assign_disabled(self):
        self.settings.carrier_on_create = False
        self.settings.set_values()
        sale_order = self._create_sale_order()
        self.assertFalse(sale_order.carrier_id)

    def test_sale_order_carrier_auto_assign_all_service(self):
        sale_order = self.env["sale.order"].create({"partner_id": self.partner.id})
        self.assertFalse(sale_order.carrier_id)


class TestSaleOrderCarrierAutoAssignOnConfirm(TestSaleOrderCarrierAutoAssignCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings.carrier_auto_assign = True
        cls._create_sale_order()
        cls.settings.set_values()
        cls.sale_order_form = Form(cls.env["sale.order"])
        cls.sale_order_form.partner_id = cls.partner
        with cls.sale_order_form.order_line.new() as line_form:
            line_form.product_id = cls.product_storable
        cls.sale_order = cls.sale_order_form.save()

    def test_sale_order_carrier_auto_assign(self):
        self.assertFalse(self.sale_order.carrier_id)
        self.sale_order.action_confirm()
        self.assertEqual(self.sale_order.state, "sale")
        self.assertEqual(self.sale_order.carrier_id, self.delivery_local_delivery)
        delivery_line = self.sale_order.order_line.filtered(
            lambda line: line.is_delivery
        )
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
