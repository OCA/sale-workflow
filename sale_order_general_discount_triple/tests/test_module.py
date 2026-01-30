from unittest.mock import patch

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestModule(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        group_discount = cls.env.ref("sale.group_discount_per_so_line")
        cls.env["res.users"].browse(1).group_ids |= group_discount
        cls.env.user.group_ids |= group_discount
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test Partner", "sale_discount": 10}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product 04",
                "default_code": "FURN_0096",
                "standard_price": 500.0,
                "weight": 0.01,
            }
        )
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test multi-currency",
                "currency_id": cls.env.ref("base.USD").id,
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "1_product",
                            "compute_price": "percentage",
                            "product_tmpl_id": cls.product.product_tmpl_id.id,
                            "percent_price": 20,
                        },
                    ),
                ],
            }
        )
        cls.env["ir.config_parameter"].create(
            {
                "key": "sale_order_general_discount_triple.general_discount",
                "value": "discount2",
            }
        )
        cls.env["ir.config_parameter"].create(
            {
                "key": "sale_order_general_discount_triple.pricelist_discount",
                "value": "discount1",
            }
        )
        cls.delivery_product = cls.env["product.product"].create(
            {
                "name": "Delivery Product",
                "type": "service",
            }
        )
        cls.carrier = cls.env["delivery.carrier"].create(
            {
                "name": "Test Carrier",
                "product_id": cls.delivery_product.id,
            }
        )

    def _create_sale_order(self):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
                "order_line": [Command.create({"product_id": self.product.id})],
            }
        )

    def test_action_result(self):
        sale_order = self._create_sale_order()
        sale_order.order_line.product_uom_qty = 2
        for line in sale_order.order_line.filtered(
            lambda line: line.product_id == self.product
        ):
            self.assertEqual(line.discount2, 10)
            self.assertEqual(line.discount1, 20)

    def test_onchange_general_discount(self):
        sale_order = self._create_sale_order()
        sale_order.general_discount = 30
        sale_order.onchange_general_discount()
        for line in sale_order.order_line.filtered(
            lambda line: line.product_id == self.product
        ):
            self.assertEqual(line.discount2, 30)

    def test_create_delivery_line(self):
        sale_order = self._create_sale_order()
        sale_order._create_delivery_line(self.carrier, 10.0)
        for line in sale_order.order_line.filtered(
            lambda line: line.product_id == self.product
        ):
            self.assertEqual(line.discount1, 20)
            self.assertEqual(line.discount2, 10)

    def test_recompute_prices(self):
        sale_order = self._create_sale_order()
        sale_order._recompute_prices()
        for line in sale_order.order_line.filtered(
            lambda line: line.product_id == self.product
        ):
            self.assertEqual(line.discount1, 20)
            self.assertEqual(line.discount2, 10)

    def test_discount_configurations(self):
        """Test all discount position configurations.
        This test covers the following scenarios:
        1. Default configuration: discount1 = pricelist_discount, discount2 = general_discount
        2. Custom configuration: discount1 = general_discount, discount2 = pricelist_discount
        3. Custom configuration: discount1 = general_discount, discount2 = pricelist_discount
        """  # noqa: E501
        sale_order = self._create_sale_order()
        sale_order.general_discount = 15
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_order_general_discount_triple.pricelist_discount", "discount2"
        )
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_order_general_discount_triple.general_discount", "discount1"
        )
        sale_order.order_line._compute_discount1()
        sale_order.order_line._compute_discount2()
        for line in sale_order.order_line.filtered(
            lambda line: line.product_id == self.product
        ):
            self.assertEqual(line.discount1, 15)
            self.assertEqual(line.discount2, 20)
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_order_general_discount_triple.pricelist_discount", "discount3"
        )
        sale_order.order_line._compute_discount3()
        for line in sale_order.order_line.filtered(
            lambda line: line.product_id == self.product
        ):
            self.assertEqual(line.discount3, 20)
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_order_general_discount_triple.pricelist_discount", "discount2"
        )
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_order_general_discount_triple.general_discount", "discount2"
        )
        sale_order.order_line._compute_discount1()
        for line in sale_order.order_line.filtered(
            lambda line: line.product_id == self.product
        ):
            self.assertEqual(line.discount1, 0.0)
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_order_general_discount_triple.general_discount", "discount2"
        )
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_order_general_discount_triple.pricelist_discount", "discount1"
        )

    def test_bypass_general_discount(self):
        """Test the bypass_general_discount flag on product."""
        self.product.bypass_general_discount = True
        sale_order = self._create_sale_order()
        sale_order.general_discount = 30
        sale_order.onchange_general_discount()
        for line in sale_order.order_line.filtered(
            lambda line: line.product_id == self.product
        ):
            self.assertEqual(line.discount2, 0.0)

    def test_reward_line_coverage(self):
        """Test that reward lines are correctly identified and skipped."""
        sale_order = self._create_sale_order()
        line = sale_order.order_line[0]
        with patch.object(
            type(self.env["sale.order.line"]),
            "_check_is_reward_line",
            return_value=True,
        ):
            line.discount1 = 10.0
            line._compute_discount1()
            self.assertEqual(line.discount1, 0.0)
            line.discount2 = 10.0
            line._compute_discount2()
            self.assertEqual(line.discount2, 0.0)
            line.discount3 = 10.0
            line._compute_discount3()
            self.assertEqual(line.discount3, 0.0)

    def test_edge_case_lines(self):
        """Test lines without products (sections/notes)."""
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
                "general_discount": 0.0,  # Ensure no general discount
                "order_line": [
                    Command.create({"name": "Section", "display_type": "line_section"}),
                    Command.create({"name": "Note", "display_type": "line_note"}),
                ],
            }
        )
        for line in sale_order.order_line:
            self.assertEqual(line.discount1, 0.0)
            self.assertEqual(line.discount2, 0.0)
            self.assertEqual(line.discount3, 0.0)
