# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import exceptions
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleOrderConfirmPartial(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["ir.config_parameter"].set_param(
            "sale_order_confirm_partial.enabled", True
        )
        cls.sale_order = cls.env["sale.order"].create(
            {
                "name": "SO-TEST",
                "partner_id": cls.env.ref("base.res_partner_1").id,
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )
        cls.so_line_1 = cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order.id,
                "product_id": cls.env.ref("product.product_product_6").id,
                "product_uom_qty": 10,
                "price_unit": 100,
            }
        )
        cls.so_line_2 = cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order.id,
                "product_id": cls.env.ref("product.product_product_7").id,
                "product_uom_qty": 7,
                "price_unit": 200,
            }
        )

    def test_confirmation_with_save_unconfirmed_all(self):
        self.env["ir.config_parameter"].set_param(
            "sale_order_confirm_partial.save_unconfirmed", True
        )
        # Confirm SO partially
        self.env["sale.order.confirm.partial"].create(
            {"sale_order_id": self.sale_order.id, "mode": "all"}
        ).action_confirm()

        # Check SO state
        self.assertEqual(self.sale_order.state, "sale", "Sale order is not confirmed")

        # Since we have confirmed all of the lines, there is no need to save
        # the unconfirmed part of SO
        unconfirmed_so = self.env["sale.order"].search([("name", "like", "SO-TEST-U")])
        self.assertFalse(
            unconfirmed_so,
            "Unconfirmed part of SO has been created when all of lines were confirmed.",
        )

        # Check original order lines quantities
        # (they should stay the same)
        self.assertEqual(
            self.so_line_1.product_uom_qty,
            10,
            "Original order line 1 qty is wrong",
        )
        self.assertEqual(
            self.so_line_2.product_uom_qty,
            7,
            "Original order line 2 qty is wrong",
        )

    def test_confirmation_with_save_unconfirmed_selected(self):
        self.env["ir.config_parameter"].set_param(
            "sale_order_confirm_partial.save_unconfirmed", True
        )
        # Confirm SO partially
        self.env["sale.order.confirm.partial"].create(
            {
                "sale_order_id": self.sale_order.id,
                "mode": "selected",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "so_line_id": self.so_line_1.id,
                            "confirmed_qty": 4,
                        },
                    ),
                ],
            }
        ).action_confirm()

        # Check SO state
        self.assertEqual(self.sale_order.state, "sale", "Sale order is not confirmed")

        # Since we have confirmed selected line, we need to save
        # the unconfirmed part of SO
        unconfirmed_so = self.env["sale.order"].search([("name", "like", "SO-TEST-U")])
        self.assertTrue(
            unconfirmed_so,
            "Unconfirmed part of SO hasn't been created when order was confirmed partially.",
        )
        # Check unconfirmed SO status
        self.assertEqual(
            unconfirmed_so.state, "cancel", "Unconfirmed SO is not in cancel state"
        )
        # Check unconfirmed order lines quantities
        # (they should be equal to statement original_qty - confirmed_qty)
        self.assertEqual(
            unconfirmed_so.order_line.filtered(
                lambda x: x.so_line_id == self.so_line_1
            ).product_uom_qty,
            6,
            "Unconfirmed part of order line 1 qty is wrong",
        )
        self.assertEqual(
            unconfirmed_so.order_line.filtered(
                lambda x: x.so_line_id == self.so_line_2
            ).product_uom_qty,
            7,
            "Unconfirmed part of order line 2 qty is wrong",
        )

        # Check original order lines quantities
        # (they should be reduced accordingly to the confirmed quantities)
        self.assertEqual(
            self.so_line_1.product_uom_qty,
            4,
            "Original order line 1 qty is wrong",
        )
        self.assertEqual(
            self.so_line_2.product_uom_qty,
            0,
            "Original order line 2 qty is wrong",
        )

    def test_confirmation_without_save_unconfirmed_selected(self):
        # Confirm SO partially
        self.env["sale.order.confirm.partial"].create(
            {
                "sale_order_id": self.sale_order.id,
                "mode": "selected",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "so_line_id": self.so_line_1.id,
                            "confirmed_qty": 4,
                        },
                    ),
                ],
            }
        ).action_confirm()

        # Check SO state
        self.assertEqual(self.sale_order.state, "sale", "Sale order is not confirmed")

        # Since we have confirmed selected line, we need to save
        # the unconfirmed part of SO (but it's disabled)
        unconfirmed_so = self.env["sale.order"].search([("name", "like", "SO-TEST-U")])
        self.assertFalse(
            unconfirmed_so,
            "Unconfirmed part of SO has been created but settings option is disabled.",
        )

        # Check original order lines quantities
        # (they should be reduced accordingly to the confirmed quantities)
        self.assertEqual(
            self.so_line_1.product_uom_qty,
            4,
            "Original order line 1 qty is wrong",
        )
        self.assertEqual(
            self.so_line_2.product_uom_qty,
            0,
            "Original order line 2 qty is wrong",
        )

    def test_sale_order_confirm_errors(self):
        # Try to create confirmation for quantity less the zero
        with self.assertRaises(exceptions.ValidationError):
            self.env["sale.order.confirm.partial"].create(
                {
                    "sale_order_id": self.sale_order.id,
                    "mode": "selected",
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "so_line_id": self.so_line_1.id,
                                "confirmed_qty": -4,
                            },
                        ),
                    ],
                }
            )
        # Try to create confirmation for quantity greater than original quantity
        with self.assertRaises(exceptions.ValidationError):
            self.env["sale.order.confirm.partial"].create(
                {
                    "sale_order_id": self.sale_order.id,
                    "mode": "selected",
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "so_line_id": self.so_line_1.id,
                                "confirmed_qty": 15,
                            },
                        ),
                    ],
                }
            )
