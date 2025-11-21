# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.sale_order_team_from_product.models.res_config_settings import (
    _PARAM_SET_FROM_PRODUCTS,
    _PARAM_SKIP_IF_SET,
)


@tagged("post_install", "-at_install")
class TestSaleOrderTeamFromProduct(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ICP = cls.env["ir.config_parameter"].sudo()
        cls.SaleOrder = cls.env["sale.order"]
        cls.ResConfigSettings = cls.env["res.config.settings"]

        cls.partner = cls.env.ref("base.res_partner_2")

        # Create two sales teams
        cls.team_a = cls.env["crm.team"].create(
            {"name": "Team A", "company_id": cls.env.company.id}
        )
        cls.team_b = cls.env["crm.team"].create(
            {"name": "Team B", "company_id": cls.env.company.id}
        )

        # Products without and with sales teams
        ProductTemplate = cls.env["product.template"]

        # Product without team
        template_no_team = ProductTemplate.create(
            {
                "name": "No Team Product",
                "type": "service",
                "list_price": 10.0,
            }
        )
        cls.product_no_team = template_no_team.product_variant_id

        # Two products with Team A
        product_template_a1 = ProductTemplate.create(
            {
                "name": "Team A Product 1",
                "type": "service",
                "list_price": 20.0,
                "sales_team_id": cls.team_a.id,
            }
        )
        product_template_a2 = ProductTemplate.create(
            {
                "name": "Team A Product 2",
                "type": "service",
                "list_price": 30.0,
                "sales_team_id": cls.team_a.id,
            }
        )
        cls.product_team_a_1 = product_template_a1.product_variant_id
        cls.product_team_a_2 = product_template_a2.product_variant_id

        # Product with Team B
        product_template_b1 = ProductTemplate.create(
            {
                "name": "Team B Product",
                "type": "service",
                "list_price": 40.0,
                "sales_team_id": cls.team_b.id,
            }
        )
        cls.product_team_b_1 = product_template_b1.product_variant_id

    def _set_config(self, enabled, skip_if_set):
        """Convenience helper to configure module ICP flags."""
        self.ICP.set_param(_PARAM_SET_FROM_PRODUCTS, "True" if enabled else "False")
        self.ICP.set_param(_PARAM_SKIP_IF_SET, "True" if skip_if_set else "False")

    def _create_order(self, products, team=None):
        """Create a quotation with given products.

        :param products: list of product.product records
        :param team: optional crm.team record to set on order
        """
        order_vals = {
            "partner_id": self.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "product_id": product.id,
                        "product_uom_qty": 1.0,
                    },
                )
                for product in products
            ],
        }
        if team:
            order_vals["team_id"] = team.id
        return self.SaleOrder.create(order_vals)

    def test_res_config_settings_roundtrip(self):
        """Settings wizard must store flags used by SaleOrder helper."""
        # 1) Set both flags to True
        settings = self.ResConfigSettings.create(
            {
                "set_sales_team_from_products": True,
                "skip_sales_team_if_set": True,
            }
        )
        settings.set_values()

        enabled, skip_if_set = self.SaleOrder._get_sales_team_from_product_config()
        self.assertTrue(enabled)
        self.assertTrue(skip_if_set)

        # 2) Set both flags to False and save again
        settings = self.ResConfigSettings.create(
            {
                "set_sales_team_from_products": False,
                "skip_sales_team_if_set": False,
            }
        )
        settings.set_values()

        enabled, skip_if_set = self.SaleOrder._get_sales_team_from_product_config()
        self.assertFalse(enabled)
        self.assertFalse(skip_if_set)

    def test_get_sales_team_from_product_config(self):
        """_get_sales_team_from_product_config must reflect ICP flags."""
        # Case 1: both False
        self._set_config(enabled=False, skip_if_set=False)
        enabled, skip_if_set = self.SaleOrder._get_sales_team_from_product_config()
        self.assertFalse(enabled)
        self.assertFalse(skip_if_set)

        # Case 2: enabled=True, skip_if_set=True
        self._set_config(enabled=True, skip_if_set=True)
        enabled, skip_if_set = self.SaleOrder._get_sales_team_from_product_config()
        self.assertTrue(enabled)
        self.assertTrue(skip_if_set)

    def test_get_sales_team_from_products_no_team(self):
        """If no lines have a team, method must return False."""
        order = self._create_order([self.product_no_team])
        team = order._get_sales_team_from_products()
        self.assertFalse(team)

    def test_get_sales_team_from_products_same_team(self):
        """If all products have the same team, that team must be returned."""
        order = self._create_order([self.product_team_a_1, self.product_team_a_2])
        team_id = order._get_sales_team_from_products()
        self.assertEqual(team_id, self.team_a.id)

    def test_get_sales_team_from_products_different_teams(self):
        """If products have different teams, method must return False."""
        order = self._create_order([self.product_team_a_1, self.product_team_b_1])
        team = order._get_sales_team_from_products()
        self.assertFalse(team)

    def test_create_no_feature_enabled_does_not_change_team(self):
        """When feature disabled, create must not change team."""
        self._set_config(enabled=False, skip_if_set=False)
        order = self._create_order([self.product_team_a_1, self.product_team_a_2])
        default_team = self.env.ref("sales_team.team_sales_department")
        # Team stays whatever Odoo default sets (False, unless other logic)
        self.assertEqual(order.team_id, default_team)

    def test_create_sets_team_from_products_when_enabled(self):
        """When enabled, create must set team from products."""
        self._set_config(enabled=True, skip_if_set=False)
        order = self._create_order([self.product_team_a_1, self.product_team_a_2])
        self.assertEqual(order.team_id, self.team_a)

    def test_create_respects_skip_if_team_already_set(self):
        """When skip_if_set=True and team already set, keep existing team."""
        self._set_config(enabled=True, skip_if_set=True)
        # Pre-set team on order, but products point to team_a
        order = self._create_order(
            [self.product_team_a_1, self.product_team_a_2], team=self.team_b
        )
        # Existing team must be preserved
        self.assertEqual(order.team_id, self.team_b)

    def test_write_skips_when_irrelevant_fields_changed(self):
        """Changing unrelated fields must not affect the Sales Team."""
        self._set_config(enabled=True, skip_if_set=False)
        order = self._create_order([self.product_team_a_1, self.product_team_a_2])
        self.assertEqual(order.team_id, self.team_a)

        # Change an unrelated field only
        order.write({"client_order_ref": "INTERNAL-REF"})
        # Team must remain untouched
        self.assertEqual(order.team_id, self.team_a)

    def test_write_applies_team_when_lines_change(self):
        """write() must apply team from products when lines change."""
        # Start with config enabled and no skip
        self._set_config(enabled=True, skip_if_set=False)
        # Create order with product without team
        order = self._create_order([self.product_no_team])
        default_team = self.env.ref("sales_team.team_sales_department")
        self.assertEqual(order.team_id, default_team)

        # Now replace lines with products that have Team A
        order.write(
            {
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_team_a_1.id,
                            "product_uom_qty": 1.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_team_a_2.id,
                            "product_uom_qty": 1.0,
                        },
                    ),
                ]
            }
        )
        self.assertEqual(order.team_id, self.team_a)

    def test_write_respects_skip_if_team_already_set(self):
        """With skip_if_set=True, changing lines must not override existing team."""
        self._set_config(enabled=True, skip_if_set=True)
        # Initial order with Team B and product without team
        order = self._create_order([self.product_no_team], team=self.team_b)

        # Add lines with Team A products
        order.write(
            {
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_team_a_1.id,
                            "product_uom_qty": 1.0,
                        },
                    )
                ]
            }
        )
        # Existing Team B must be preserved due to skip_if_set=True
        self.assertEqual(order.team_id, self.team_b)

    def test_apply_sales_team_ignored_for_non_draft_sent(self):
        """_apply_sales_team_from_products must not touch confirmed orders."""
        self._set_config(enabled=True, skip_if_set=False)
        order = self._create_order([self.product_team_a_1, self.product_team_a_2])
        # Confirm the order, changing its state
        order.action_confirm()
        self.assertNotIn(order.state, ("draft", "sent"))

        # Manually clear team_id to see if apply() tries to change it
        order.team_id = False
        order._apply_sales_team_from_products(skip_if_set=False)
        # For non draft/sent state, team must remain unchanged
        self.assertFalse(order.team_id)

    def test_apply_sales_team_no_team_when_conflict(self):
        """_apply_sales_team_from_products must do nothing when teams conflict."""
        self._set_config(enabled=True, skip_if_set=False)
        order = self._create_order([self.product_team_a_1, self.product_team_b_1])
        default_team = self.env.ref("sales_team.team_sales_department")
        self.assertEqual(order.team_id, default_team)

        # Conflict between Team A and B => _get_sales_team_from_products returns False
        order._apply_sales_team_from_products(skip_if_set=False)
        self.assertEqual(order.team_id, default_team)
