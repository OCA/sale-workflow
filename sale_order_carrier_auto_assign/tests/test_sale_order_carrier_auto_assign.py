# Copyright 2020 Camptocamp SA
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.fields import Command
from odoo.tests import Form

from .common import TestSaleOrderCarrierAutoAssignCommon


class TestSaleOrderCarrierAutoAssignOnCreate(TestSaleOrderCarrierAutoAssignCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings = cls.settings.sudo()
        cls.settings.carrier_on_create = True
        cls.settings.carrier_auto_assign = False
        cls.settings.set_values()

    def test_sale_order_carrier_auto_assign_no_carrier(self):
        self.partner.sudo().property_delivery_carrier_id = False
        sale_order = self._create_sale_order().sudo()
        self.assertFalse(sale_order.carrier_id)

    def test_sale_order_carrier_auto_assign_onchange(self):
        sale_order = self._create_sale_order().sudo()
        self.assertEqual(sale_order.carrier_id, self.delivery_local_delivery)
        # Change partner and check carrier change
        new_carrier = self.delivery_local_delivery.sudo().copy()
        new_partner = (
            self.env["res.partner"]
            .sudo()
            .create(
                {
                    "name": "Test partner 2",
                    "property_delivery_carrier_id": new_carrier.id,
                }
            )
        )
        sale = Form(sale_order)
        sale.partner_id = new_partner
        self.assertEqual(sale.carrier_id, new_carrier)

    def test_sale_order_carrier_auto_assign_create(self):
        sale_order = (
            self.env["sale.order"]
            .sudo()
            .create(
                {
                    "partner_id": self.partner.id,
                    "order_line": [
                        Command.create(
                            {
                                "product_id": self.product_storable.id,
                                "product_uom_qty": 1.0,
                                "price_unit": 100.0,
                            }
                        )
                    ],
                }
            )
        )
        self.assertEqual(sale_order.carrier_id, self.delivery_local_delivery)

    def test_sale_order_carrier_auto_assign_unavailable_carrier(self):
        unavailable_country = (
            self.env["res.country"]
            .sudo()
            .create(
                {
                    "name": "Unavailable Carrier Country",
                    "code": "XA",
                }
            )
        )
        unavailable_carrier = self.delivery_local_delivery.sudo().copy(
            {
                "name": "Unavailable Carrier",
                "country_ids": [Command.set(unavailable_country.ids)],
            }
        )
        self.partner.sudo().property_delivery_carrier_id = unavailable_carrier
        sale_order = (
            self.env["sale.order"]
            .sudo()
            .create(
                {
                    "partner_id": self.partner.id,
                    "order_line": [
                        Command.create(
                            {
                                "product_id": self.product_storable.id,
                                "product_uom_qty": 1.0,
                                "price_unit": 100.0,
                            }
                        )
                    ],
                }
            )
        )
        self.assertFalse(sale_order.carrier_id)

    def test_sale_order_carrier_auto_assign_create_2steps_from_order(self):
        """Test carrier is set when a product line is added"""
        sale_order = (
            self.env["sale.order"]
            .sudo()
            .create(
                {
                    "partner_id": self.partner.id,
                }
            )
        )
        sale_order.sudo().write(
            {
                "order_line": [
                    Command.create({"product_id": self.product_storable.id})
                ],
            }
        )
        self.assertEqual(sale_order.carrier_id, self.delivery_local_delivery)

    def test_sale_order_carrier_auto_assign_create_2steps_from_line(self):
        """Test carrier is set when a product line is added"""
        sale_order = (
            self.env["sale.order"]
            .sudo()
            .create(
                {
                    "partner_id": self.partner.id,
                }
            )
        )
        self.env["sale.order.line"].sudo().create(
            {
                "order_id": sale_order.id,
                "product_id": self.product_storable.id,
            }
        )
        self.assertEqual(sale_order.carrier_id, self.delivery_local_delivery)

    def test_sale_order_carrier_auto_assign_create_3steps_from_line(self):
        """Test carrier is set when a product line is added"""
        sale_order = (
            self.env["sale.order"]
            .sudo()
            .create(
                {
                    "partner_id": self.partner.id,
                }
            )
        )
        sale_order_line = (
            self.env["sale.order.line"]
            .sudo()
            .create(
                {
                    "order_id": sale_order.id,
                    "product_id": self.product_service.id,
                }
            )
        )
        sale_order_line.sudo().product_id = self.product_storable
        self.assertEqual(sale_order.carrier_id, self.delivery_local_delivery)

    def test_sale_order_carrier_auto_assign_disabled(self):
        self.settings.sudo().carrier_on_create = False
        self.settings.sudo().set_values()
        sale_order = self._create_sale_order().sudo()
        self.assertFalse(sale_order.carrier_id)

    def test_sale_order_carrier_auto_assign_all_service(self):
        sale_order = (
            self.env["sale.order"].sudo().create({"partner_id": self.partner.id})
        )
        self.assertFalse(sale_order.carrier_id)


class TestSaleOrderCarrierAutoAssignOnConfirm(TestSaleOrderCarrierAutoAssignCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings = cls.settings.sudo()
        cls.settings.carrier_on_create = False
        cls.settings.carrier_auto_assign = True
        cls.settings.set_values()
        cls._create_sale_order()
        cls.sale_order_form = Form(cls.env["sale.order"].sudo())
        cls.sale_order_form.partner_id = cls.partner
        with cls.sale_order_form.order_line.new() as line_form:
            line_form.product_id = cls.product_storable
        cls.sale_order = cls.sale_order_form.save().sudo()

    def test_sale_order_carrier_auto_assign(self):
        self.assertFalse(self.sale_order.sudo().carrier_id)
        self.sale_order.sudo().action_confirm()
        self.assertEqual(self.sale_order.state, "sale")
        self.assertEqual(
            self.sale_order.carrier_id, self.delivery_local_delivery.sudo()
        )
        delivery_line = self.sale_order.order_line.filtered(
            lambda line: line.is_delivery
        )
        delivery_rate = self.delivery_local_delivery.rate_shipment(self.sale_order)
        self.assertEqual(delivery_line.price_unit, delivery_rate["price"])

    def test_sale_order_carrier_auto_assign_free_over(self):
        self.delivery_local_delivery.sudo().free_over = True
        self.delivery_local_delivery.sudo().amount = 1.0
        sale_order = self._create_sale_order().sudo()
        sale_order.action_confirm()
        delivery_line = sale_order.order_line.filtered(lambda line: line.is_delivery)
        delivery_rate = self.delivery_local_delivery.rate_shipment(sale_order)
        self.assertEqual(delivery_rate["price"], 0.0)
        self.assertEqual(delivery_line.price_unit, delivery_rate["price"])

    def test_sale_order_carrier_auto_assign_disabled(self):
        self.assertEqual(
            self.partner.sudo().property_delivery_carrier_id,
            self.delivery_local_delivery.sudo(),
        )
        self.assertFalse(self.sale_order.sudo().carrier_id)
        self.settings.sudo().carrier_auto_assign = False
        self.settings.sudo().set_values()
        self.sale_order.sudo().action_confirm()
        self.assertEqual(self.sale_order.state, "sale")
        self.assertFalse(self.sale_order.sudo().carrier_id)

    def test_sale_order_carrier_auto_assign_no_carrier(self):
        self.partner.sudo().property_delivery_carrier_id = False
        self.assertFalse(self.sale_order.sudo().carrier_id)
        self.sale_order.sudo().action_confirm()
        self.assertEqual(self.sale_order.state, "sale")
        self.assertFalse(self.sale_order.sudo().carrier_id)

    def test_sale_order_carrier_auto_assign_carrier_already_set(self):
        self.assertEqual(
            self.partner.sudo().property_delivery_carrier_id,
            self.delivery_local_delivery.sudo(),
        )
        carrier = self.delivery_carrier_alternative
        self.sale_order.sudo().carrier_id = carrier
        self.sale_order.sudo().action_confirm()
        self.assertEqual(self.sale_order.state, "sale")
        self.assertEqual(self.sale_order.carrier_id, carrier)

    def test_sale_order_carrier_auto_assign_all_service(self):
        self.assertEqual(
            self.partner.sudo().property_delivery_carrier_id,
            self.delivery_local_delivery.sudo(),
        )
        self.sale_order.sudo().order_line.product_id = self.product_service
        self.sale_order.sudo().action_confirm()
        self.assertEqual(self.sale_order.state, "sale")
        self.assertFalse(self.sale_order.sudo().carrier_id)

    def test_sale_order_carrier_onchange_no_order_line(self):
        """Ensure no error occurs when changing partner on an empty sale order."""
        sale_order = (
            self.env["sale.order"].sudo().create({"partner_id": self.partner.id})
        )
        new_partner = self.env["res.partner"].sudo().create({"name": "Another Partner"})
        sale_order.partner_id = new_partner
        self.assertFalse(
            sale_order.carrier_id,
            "Carrier should not be set for sale order without lines",
        )
