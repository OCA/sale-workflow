# Copyright 2020 Camptocamp SA
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from unittest.mock import patch

from odoo.fields import Command
from odoo.tests import Form

from .common import TestSaleOrderCarrierAutoAssignCommon


class TestSaleOrderCarrierAutoAssignOnCreate(TestSaleOrderCarrierAutoAssignCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings.carrier_on_create = True
        cls.settings.carrier_auto_assign = False
        cls.settings.set_values()

    def test_sale_order_carrier_auto_assign_no_carrier(self):
        self.partner.property_delivery_carrier_id = False
        sale_order = self._create_sale_order()
        self.assertFalse(sale_order.carrier_id)

    def test_sale_order_carrier_auto_assign_onchange(self):
        sale_order = self._create_sale_order()
        self.assertEqual(sale_order.carrier_id, self.delivery_local_delivery)
        # Change partner and check carrier change
        new_carrier = self.delivery_local_delivery.copy()
        new_partner = self.env["res.partner"].create(
            {
                "name": "Test partner 2",
                "property_delivery_carrier_id": new_carrier.id,
            }
        )
        sale = Form(sale_order)
        sale.partner_id = new_partner
        self.assertEqual(sale.carrier_id, new_carrier)

    def test_sale_order_carrier_auto_assign_create(self):
        sale_order = self.env["sale.order"].create(
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
        self.assertEqual(sale_order.carrier_id, self.delivery_local_delivery)

    def test_sale_order_carrier_auto_assign_unavailable_carrier(self):
        unavailable_country = self.env["res.country"].create(
            {
                "name": "Unavailable Carrier Country",
                "code": "XA",
            }
        )
        unavailable_carrier = self.delivery_local_delivery.copy(
            {
                "name": "Unavailable Carrier",
                "country_ids": [Command.set(unavailable_country.ids)],
            }
        )
        self.partner.property_delivery_carrier_id = unavailable_carrier
        sale_order = self.env["sale.order"].create(
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
        self.assertFalse(sale_order.carrier_id)

    def test_sale_order_carrier_auto_assign_create_2steps_from_order(self):
        """Test carrier is set when a product line is added"""
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
            }
        )
        sale_order.write(
            {
                "order_line": [
                    Command.create({"product_id": self.product_storable.id})
                ],
            }
        )
        self.assertEqual(sale_order.carrier_id, self.delivery_local_delivery)

    def test_sale_order_carrier_auto_assign_create_2steps_from_line(self):
        """Test carrier is set when a product line is added"""
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
            }
        )
        self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": self.product_storable.id,
            }
        )
        self.assertEqual(sale_order.carrier_id, self.delivery_local_delivery)

    def test_sale_order_carrier_auto_assign_create_3steps_from_line(self):
        """Test carrier is set when a product line is added"""
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
            }
        )
        sale_order_line = self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": self.product_service.id,
            }
        )
        sale_order_line.product_id = self.product_storable
        self.assertEqual(sale_order.carrier_id, self.delivery_local_delivery)

    def test_sale_order_carrier_auto_assign_disabled(self):
        self.settings.carrier_on_create = False
        self.settings.set_values()
        sale_order = self._create_sale_order()
        self.assertFalse(sale_order.carrier_id)

    def test_sale_order_carrier_auto_assign_all_service(self):
        sale_order = self.env["sale.order"].create({"partner_id": self.partner.id})
        self.assertFalse(sale_order.carrier_id)

    def test_sale_order_carrier_auto_assign_set_delivery_line(self):
        """Changing the carrier keeps a single delivery line.

        Simulate a write on the order once its delivery line is removed, like
        website_sale does to reset the pickup location.
        """
        sale_order = self._create_sale_order()
        sale_order.set_delivery_line(self.delivery_local_delivery, 10.0)
        # `set_delivery_line` removes the delivery line, then sets the carrier:
        # https://github.com/odoo/odoo/blob/d0a05578/addons/delivery/models/sale_order.py#L67-L72
        # Removing the delivery line also clears the carrier of the order:
        # https://github.com/odoo/odoo/blob/d0a05578/addons/delivery/models/sale_order_line.py#L29
        # That write alone doesn't auto-assign a carrier, the delivery line
        # still exists at that point (see `delivery_set`). But any write after
        # the removal finds an order with neither carrier nor delivery line,
        # e.g. website_sale resetting the pickup location:
        # https://github.com/odoo/odoo/blob/d0a05578/addons/website_sale/models/sale_order.py#L825-L828
        # Simulate such a write, as this module doesn't depend on website_sale.
        SaleOrder = type(sale_order)
        remove_delivery_line = SaleOrder._remove_delivery_line

        def _remove_delivery_line(self):
            remove_delivery_line(self)
            self.client_order_ref = "Delivery line removed"

        with patch.object(SaleOrder, "_remove_delivery_line", _remove_delivery_line):
            sale_order.set_delivery_line(self.delivery_carrier_alternative, 15.0)
        self.assertEqual(sale_order.carrier_id, self.delivery_carrier_alternative)
        self.assertRecordValues(
            sale_order.order_line.filtered("is_delivery"),
            [{"product_id": self.delivery_carrier_alternative.product_id.id}],
        )


class TestSaleOrderCarrierAutoAssignOnConfirm(TestSaleOrderCarrierAutoAssignCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings.carrier_on_create = False
        cls.settings.carrier_auto_assign = True
        cls.settings.set_values()
        cls._create_sale_order()
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
        self.assertEqual(delivery_line.price_unit, delivery_rate["price"])

    def test_sale_order_carrier_auto_assign_free_over(self):
        self.delivery_local_delivery.free_over = True
        self.delivery_local_delivery.amount = 1.0
        sale_order = self._create_sale_order()
        sale_order.action_confirm()
        delivery_line = sale_order.order_line.filtered(lambda line: line.is_delivery)
        delivery_rate = self.delivery_local_delivery.rate_shipment(sale_order)
        self.assertEqual(delivery_rate["price"], 0.0)
        self.assertEqual(delivery_line.price_unit, delivery_rate["price"])

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
        carrier = self.delivery_carrier_alternative
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

    def test_sale_order_carrier_onchange_no_order_line(self):
        """Ensure no error occurs when changing partner on an empty sale order."""
        sale_order = self.env["sale.order"].create({"partner_id": self.partner.id})
        new_partner = self.env["res.partner"].create({"name": "Another Partner"})
        sale_order.partner_id = new_partner
        self.assertFalse(
            sale_order.carrier_id,
            "Carrier should not be set for sale order without lines",
        )
