# Copyright 2024 Akretion France (http://www.akretion.com/)
# @author: Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestForceReservation(TransactionCase):
    def setUp(self):
        super().setUp()
        self.insurance_product = self.env["product.product"].create(
            {
                "name": "insurance product",
                "type": "consu",
            }
        )
        self.company_id = self.env.ref("base.main_company")
        self.company_id.coefficient_sale_insurance = 0.02
        self.company_id.insurance_product = self.insurance_product.id
        self.partner_id = self.env.ref("base.res_partner_2")
        self.product_id = self.env.ref("sale.product_product_4f")

    def _create_sale_order(self):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_id.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        return sale_order

    def test_sale_partner_insurance(self):
        self.partner_id.company_id = self.company_id
        sale_order = self._create_sale_order()
        sale_order.action_confirm()
        self.assertEqual(len(sale_order.order_line), 2)
        self.assertEqual(sale_order.order_line[1].price_unit, 15)
        self.assertEqual(sale_order.amount_untaxed, 765)
        sale_order.order_line[0].product_uom_qty = 5
        self.assertEqual(sale_order.order_line[1].price_unit, 75)
        self.assertEqual(sale_order.amount_untaxed, 3825)

    def test_sale_partner_insurance_change_amount(self):
        self.partner_id.company_id = self.company_id
        sale_order = self._create_sale_order()
        sale_order.action_confirm()
        sale_order.order_line[0].price_unit = 500
        self.assertEqual(sale_order.order_line[1].price_unit, 10)
        self.assertEqual(sale_order.amount_untaxed, 510)

    def test_cancel_sale_order(self):
        self.partner_id.company_id = self.company_id
        sale_order = self._create_sale_order()
        sale_order.action_confirm()
        self.assertEqual(len(sale_order.order_line), 2)
        sale_order.action_cancel()
        self.assertEqual(len(sale_order.order_line), 1)
