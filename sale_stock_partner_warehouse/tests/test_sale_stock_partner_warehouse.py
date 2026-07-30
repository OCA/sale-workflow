# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestSaleStockPartnerWarehouse(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse_1 = cls.env["stock.warehouse"].create(
            {
                "name": "Base Warehouse 1",
                "reception_steps": "one_step",
                "delivery_steps": "ship_only",
                "code": "BWH1",
                "company_id": cls.company.id,
            }
        )
        cls.warehouse_2 = cls.env["stock.warehouse"].create(
            {
                "name": "Test Warehouse 2",
                "reception_steps": "one_step",
                "delivery_steps": "ship_only",
                "code": "TWH2",
                "company_id": cls.company.id,
            }
        )
        cls.shipping_partner = cls.env["res.partner"].create(
            {
                "name": "Test Shipping Address",
                "parent_id": cls.partner.id,
                "type": "delivery",
            }
        )

    def setUp(self):
        super().setUp()
        # Reset company setting before each test
        self.company.sale_warehouse_by_partner_shipping = False

    def test_01_partner_warehouse_default(self):
        """Test default warehouse logic when company setting is disabled."""
        self.partner.sale_warehouse_id = self.warehouse_1
        self.shipping_partner.sale_warehouse_id = self.warehouse_2

        with Form(self.env["sale.order"]) as order_form:
            order_form.partner_id = self.partner
        order = order_form.save()

        # Should pick main partner's warehouse because
        # sale_warehouse_by_partner_shipping is False
        self.assertEqual(order.warehouse_id, self.warehouse_1)

    def test_02_shipping_partner_warehouse_priority(self):
        """Test prioritizing shipping address warehouse when
        company setting is enabled."""
        self.company.sale_warehouse_by_partner_shipping = True
        self.partner.sale_warehouse_id = self.warehouse_1
        self.shipping_partner.sale_warehouse_id = self.warehouse_2

        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_shipping_id": self.shipping_partner.id,
            }
        )
        order._compute_warehouse_id()

        # Should pick shipping partner's warehouse when setting is enabled
        self.assertEqual(order.warehouse_id, self.warehouse_2)

    def test_03_shipping_partner_warehouse_fallback_to_partner(self):
        """Test fallback to main partner warehouse if shipping
        address has no warehouse set."""
        self.company.sale_warehouse_by_partner_shipping = True
        self.partner.sale_warehouse_id = self.warehouse_1
        self.shipping_partner.sale_warehouse_id = False

        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_shipping_id": self.shipping_partner.id,
            }
        )
        order._compute_warehouse_id()

        self.assertEqual(order.warehouse_id, self.warehouse_1)

    def test_04_no_partner_warehouse_fallback_to_super(self):
        """Test fallback to default user/company warehouse when
        neither partner has warehouse set."""
        self.partner.sale_warehouse_id = False
        self.shipping_partner.sale_warehouse_id = False

        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_shipping_id": self.shipping_partner.id,
            }
        )
        order._compute_warehouse_id()

        # Should fall back to standard Odoo default warehouse computation
        self.assertTrue(order.warehouse_id)
        self.assertNotIn(order.warehouse_id, (self.warehouse_1, self.warehouse_2))

    def test_05_non_draft_sales_order_computation(self):
        """Test computation logic for non-draft sales orders."""
        self.partner.sale_warehouse_id = self.warehouse_1

        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "state": "sale",
            }
        )
        # Explicitly call compute on non-draft order to test `to_super` branch
        order._compute_warehouse_id()
        self.assertTrue(order.warehouse_id)

    def test_06_batch_computation_mixed_orders(self):
        """Test batch computation of warehouse on mixed set of
        draft and non-draft orders."""
        self.partner.sale_warehouse_id = self.warehouse_1
        self.shipping_partner.sale_warehouse_id = self.warehouse_2
        self.company.sale_warehouse_by_partner_shipping = True

        partner_no_wh = self.env["res.partner"].create({"name": "No WH Partner"})

        order_draft_1 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_shipping_id": self.shipping_partner.id,
                "state": "draft",
            }
        )
        order_draft_2 = self.env["sale.order"].create(
            {
                "partner_id": partner_no_wh.id,
                "state": "draft",
            }
        )
        order_confirmed = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "state": "sale",
            }
        )

        orders = order_draft_1 | order_draft_2 | order_confirmed
        orders._compute_warehouse_id()

        self.assertEqual(order_draft_1.warehouse_id, self.warehouse_2)
        self.assertTrue(order_draft_2.warehouse_id)
        self.assertTrue(order_confirmed.warehouse_id)

    def test_07_res_config_settings_wizard(self):
        """Test toggling the setting via res.config.settings wizard."""
        self.assertFalse(self.company.sale_warehouse_by_partner_shipping)

        config = self.env["res.config.settings"].create(
            {
                "sale_warehouse_by_partner_shipping": True,
            }
        )
        config.execute()

        self.assertTrue(self.company.sale_warehouse_by_partner_shipping)
