# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo.exceptions import UserError
from odoo.tests.common import Form, TransactionCase


class TestSaleTaxAdjust(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Partners
        cls.partner_1 = cls.env.ref("base.res_partner_2")

        # Products
        cls.product_1 = cls.env.ref("product.product_product_1")
        # cls.product_1.purchase_method = "purchase"

        cls.company = cls.env.ref("base.main_company")
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Tax 20",
                "type_tax_use": "sale",
                "amount": 20,
            }
        )

    def _create_sale(self, price_unit, count_line):
        Sale = self.env["sale.order"]
        view_id = "sale.view_order_form"
        with Form(Sale, view=view_id) as so:
            so.partner_id = self.partner_1
            for i in range(count_line):
                with so.order_line.new() as line:
                    line.sequence = i
                    line.product_id = self.product_1
                    line.product_uom_qty = 1.0
                    line.price_unit = price_unit
        sale = so.save()
        return sale

    def test_01_sale_tax_adjust(self):
        sale = self._create_sale(100.0, 2)
        # Add tax in line
        sale.order_line[0].tax_id = [(6, 0, self.tax.ids)]
        sale.order_line[1].tax_id = [(6, 0, self.tax.ids)]
        json_vals = json.loads(sale.tax_totals_json)
        # Check amount total PO
        self.assertAlmostEqual(sale.amount_untaxed, 200)
        self.assertAlmostEqual(sale.amount_tax, 40)
        self.assertAlmostEqual(sale.amount_total, 240)
        self.assertAlmostEqual(sale.order_line[0].price_tax, 20)
        self.assertAlmostEqual(sale.order_line[1].price_tax, 20)
        # Adjust tax from 40.0 to 15.0, diff = 25
        json_vals["groups_by_subtotal"]["Untaxed Amount"][0]["tax_group_amount"] = 15.0
        with Form(sale) as s:
            s.tax_totals_json = json.dumps(json_vals)
        s.save()
        self.assertAlmostEqual(sale.order_line[0].price_tax, 1)
        self.assertAlmostEqual(sale.order_line[1].price_tax, 14)
        # Check change price_unit in line, it should auto update refresh tax
        self.assertEqual(sale.order_line[1].qty_invoiced, 0.0)
        sale.order_line[1].price_unit = 200.0
        sale.order_line[1]._onchange_line_without_tax()
        self.assertAlmostEqual(sale.order_line[0].price_tax, 20)
        # NOTE: Line tax adjust will auto update for test script only.
        self.assertAlmostEqual(sale.order_line[1].price_tax, 40)

        # Check adjust tax less than count line
        json_vals["groups_by_subtotal"]["Untaxed Amount"][0]["tax_group_amount"] = 1.0
        with self.assertRaises(UserError):
            with Form(sale) as s:
                s.tax_totals_json = json.dumps(json_vals)
