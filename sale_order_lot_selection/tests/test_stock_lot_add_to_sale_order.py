# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import TransactionCase


class TestAddLotToSaleOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale = cls.env.ref("sale_order_lot_selection.sale1")
        cls.sale_empty = cls.env["sale.order"].create(
            {
                "partner_id": cls.sale.partner_id.id,
                "user_id": cls.env.ref("base.user_admin").id,
            }
        )
        cls.lot_cable = cls.env.ref("sale_order_lot_selection.lot_cable")
        cls.env["ir.config_parameter"].sudo().set_param(
            "sale_order_lot_selection.allow_generate_from_lots", True
        )

    def test_create_sale_order_with_lots(self):
        """Test creating a new sale order from selected lot via wizard."""
        wizard = self.env["stock.lot.sale.order.wizard"].create(
            {
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "lot_id": self.lot_cable.id,
                            "quantity": self.lot_cable.product_qty,
                        },
                    )
                ]
            }
        )
        wizard.partner_id = self.sale.partner_id

        wizard.action_create_sale_order()

        sale_order = wizard.sale_order_id
        self.assertTrue(sale_order, "Sale Order was not created")
        self.assertEqual(sale_order.partner_id, self.sale.partner_id)
        self.assertEqual(sale_order.order_line.lot_id, self.lot_cable)
        self.assertEqual(sale_order.order_line.product_id, self.lot_cable.product_id)

    def test_add_lots_to_existing_sale_order(self):
        """Test adding selected lots to an existing sale order."""
        wizard = self.env["stock.lot.sale.order.wizard"].create(
            {
                "sale_order_id": self.sale_empty.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "lot_id": self.lot_cable.id,
                            "quantity": self.lot_cable.product_qty,
                        },
                    )
                ],
            }
        )

        wizard.action_add_lots_to_sale_order()

        sale_order = self.sale_empty
        lines = sale_order.order_line.filtered(lambda l: l.lot_id == self.lot_cable)
        self.assertTrue(lines, "Lot was not added to Sale Order")
        self.assertEqual(lines.product_id, self.lot_cable.product_id)
        self.assertEqual(lines.product_uom_qty, self.lot_cable.product_qty)

    def test_error_if_no_partner_on_create(self):
        """Test that wizard raises error when trying to create sale order without partner."""
        wizard = self.env["stock.lot.sale.order.wizard"].create(
            {
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "lot_id": self.lot_cable.id,
                            "quantity": self.lot_cable.product_qty,
                        },
                    )
                ]
            }
        )

        with self.assertRaises(ValidationError):
            wizard.action_create_sale_order()

    def test_error_if_no_sale_order_on_add(self):
        """Test error when adding lots without sale order selection."""
        wizard = self.env["stock.lot.sale.order.wizard"].create(
            {
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "lot_id": self.lot_cable.id,
                            "quantity": self.lot_cable.product_qty,
                        },
                    )
                ]
            }
        )

        with self.assertRaises(ValidationError):
            wizard.action_add_lots_to_sale_order()

    def test_not_allowed_generate_from_lots(self):
        """Test that wizard raises error when generation from lots is not allowed"""
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_order_lot_selection.allow_generate_from_lots", False
        )

        with self.assertRaises(AccessError):
            self.lot_cable.action_generate_sale_order()

        self.env["ir.config_parameter"].sudo().set_param(
            "sale_order_lot_selection.allow_generate_from_lots", True
        )

        result = self.lot_cable.action_generate_sale_order()
        self.assertTrue(
            result, "Wizard should open when generation from lots is allowed"
        )
