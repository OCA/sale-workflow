# Copyright 2017 Tecnativa - Jairo Llopis
# Copyright 2020 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError

from .test_recommendation_common import RecommendationCase


class RecommendationCaseTests(RecommendationCase):
    def test_recommendations(self):
        """Recommendations are OK."""
        self.new_so.order_line = [
            (
                0,
                0,
                {
                    "product_id": self.prod_1.id,
                    "product_uom_qty": 3,
                    "qty_delivered_method": "manual",
                },
            )
        ]
        self.new_so.order_line.product_id_change()
        wizard = self.wizard()
        # Order came in from context
        self.assertEqual(wizard.order_id, self.new_so)
        self.assertEqual(len(wizard.line_ids), 3)
        self.assertEqual(wizard.line_ids[0].product_id, self.prod_2)
        self.assertEqual(wizard.line_ids[1].product_id, self.prod_1)
        self.assertEqual(wizard.line_ids[2].product_id, self.prod_3)
        # Product 2 is first
        wiz_line_prod2 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_2)
        self.assertEqual(wiz_line_prod2.times_delivered, 2)
        self.assertEqual(wiz_line_prod2.units_delivered, 100)
        self.assertEqual(wiz_line_prod2.units_included, 0)
        # Product 1 appears second
        wiz_line_prod1 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_1)
        self.assertEqual(wiz_line_prod1.times_delivered, 1)
        self.assertEqual(wiz_line_prod1.units_delivered, 25)
        self.assertEqual(wiz_line_prod1.units_included, 3)
        # Product 3 appears third
        wiz_line_prod3 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_3)
        self.assertEqual(wiz_line_prod3.times_delivered, 1)
        self.assertEqual(wiz_line_prod3.units_delivered, 100)
        self.assertEqual(wiz_line_prod3.units_included, 0)
        # Only 1 product if limited as such
        wizard.line_amount = 1
        wizard._generate_recommendations()
        self.assertEqual(len(wizard.line_ids), 2)

    def test_recommendations_archived_product(self):
        self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
            }
        )
        self.prod_1.active = False
        self.prod_2.sale_ok = False
        wizard = self.wizard()
        wizard._generate_recommendations()
        self.assertNotIn(self.prod_1, wizard.line_ids.mapped("product_id"))
        self.assertNotIn(self.prod_2, wizard.line_ids.mapped("product_id"))

    def test_transfer(self):
        """Products get transferred to SO."""
        qty = 10
        wizard = self.wizard()
        wiz_line_prod1 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_1)
        wiz_line_prod1.units_included = qty
        wizard.action_accept()
        self.assertEqual(len(self.new_so.order_line), 1)
        self.assertEqual(self.new_so.order_line.product_id, self.prod_1)
        self.assertEqual(self.new_so.order_line.product_uom_qty, qty)
        # No we confirm the SO
        self.new_so.action_confirm()
        wizard = self.wizard()
        wiz_line = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_1)
        wiz_line.units_included = 0
        # The confirmed line can't be deleted
        with self.assertRaises(UserError):
            wizard.action_accept()
        # Deliver items and invoice the order
        self.new_so.order_line.qty_delivered = qty
        adv_wiz = (
            self.env["sale.advance.payment.inv"]
            .with_context(active_ids=[self.new_so.id])
            .create(
                {
                    "advance_payment_method": "delivered",
                }
            )
        )
        adv_wiz.with_context(open_invoices=True).create_invoices()
        self.new_so.invoice_ids.action_post()
        # Open the wizard and add more product qty
        wizard = self.wizard()
        wiz_line = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_1)
        wiz_line.units_included = qty + 2
        wizard.action_accept()
        # Deliver extra qty and make a new invoice
        self.new_so.order_line.qty_delivered = qty + 2
        adv_wiz = (
            self.env["sale.advance.payment.inv"]
            .with_context(active_ids=[self.new_so.id])
            .create(
                {
                    "advance_payment_method": "delivered",
                }
            )
        )
        adv_wiz.with_context(open_invoices=True).create_invoices()
        self.assertEqual(2, len(self.new_so.invoice_ids))
        self.assertEqual(2, self.new_so.invoice_ids[-1].invoice_line_ids.quantity)

    def test_recommendations_price_origin(self):
        # Display product price from pricelist
        wizard = self.wizard()
        wizard.sale_recommendation_price_origin = "pricelist"
        wiz_line_prod1 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_1)
        self.assertEqual(wiz_line_prod1.price_unit, 25.00)
        wiz_line_prod2 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_2)
        self.assertEqual(wiz_line_prod2.price_unit, 50.00)
        wiz_line_prod3 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_3)
        self.assertEqual(wiz_line_prod3.price_unit, 75.00)

        # Display product price from last sale order price
        wizard.sale_recommendation_price_origin = "last_sale_price"
        wiz_line_prod1 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_1)
        self.assertEqual(wiz_line_prod1.price_unit, 24.50)
        wiz_line_prod2 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_2)
        self.assertEqual(wiz_line_prod2.price_unit, 49.50)
        wiz_line_prod3 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_3)
        self.assertEqual(wiz_line_prod3.price_unit, 74.50)

        # Change confirmation date in order2
        self.order2.date_order = "2021-05-07"
        wizard.sale_recommendation_price_origin = "pricelist"
        wizard.sale_recommendation_price_origin = "last_sale_price"
        wiz_line_prod2 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_2)
        self.assertEqual(wiz_line_prod2.price_unit, 89.00)

    def test_recommendations_last_sale_price_to_sale_order(self):
        # Display product price from last sale order price
        wizard = self.wizard()
        wizard.sale_recommendation_price_origin = "last_sale_price"
        wiz_line_prod1 = wizard.line_ids.filtered(lambda x: x.product_id == self.prod_1)
        wiz_line_prod1.units_included = 1.0
        wizard.action_accept()
        so_line_prod1 = wizard.order_id.order_line.filtered(
            lambda x: x.product_id == self.prod_1
        )
        self.assertEqual(so_line_prod1.price_unit, 24.50)
        # If I update sale order line price unit this price can not bw updated
        # by wizard
        so_line_prod1.price_unit = 60.0
        wiz_line_prod1.units_included = 3
        wizard.action_accept()
        self.assertEqual(so_line_prod1.price_unit, 60.0)

    def test_recommendation_delivery_address(self):
        self.new_so.partner_shipping_id = self.partner_delivery
        wizard = self.wizard()
        wizard.use_delivery_address = True
        wizard._generate_recommendations()
        self.assertEqual(len(wizard.line_ids), 1)
        self.assertEqual(wizard.line_ids[0].product_id, self.prod_2)
