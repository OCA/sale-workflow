# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.account_invoice_custom_rounding.tests.common import (
    TestAccountInvoiceCustomRoundingCommon,
)


class TestSaleCustomRounding(TestAccountInvoiceCustomRoundingCommon):
    def create_sale_order(self):
        sale_order = self.env["sale.order"].create(
            {
                "company_id": self.company.id,
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 7757.68,
                            "tax_id": [(6, 0, [self.tax.id])],
                        },
                    ),
                    (
                        0,
                        False,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 4710.88,
                            "tax_id": [(6, 0, [self.tax.id])],
                        },
                    ),
                ],
            }
        )
        return sale_order

    def test_base_case_company_globally(self):
        self.company.write({"tax_calculation_rounding_method": "round_globally"})
        sale_order = self.create_sale_order()
        self.assertFalse(sale_order.tax_calculation_rounding_method)
        self.assertAlmostEqual(sale_order.amount_total, 15086.96, places=2)
        sale_order.action_confirm()
        invoice = sale_order._create_invoices()
        self.assertFalse(invoice.tax_calculation_rounding_method)
        self.assertAlmostEqual(invoice.amount_total, 15086.96, places=2)

    def test_base_case_company_per_line(self):
        self.company.write({"tax_calculation_rounding_method": "round_per_line"})
        sale_order = self.create_sale_order()
        self.assertFalse(sale_order.tax_calculation_rounding_method)
        self.assertAlmostEqual(sale_order.amount_total, 15086.95, places=2)
        sale_order.action_confirm()
        invoice = sale_order._create_invoices()
        self.assertFalse(invoice.tax_calculation_rounding_method)
        self.assertAlmostEqual(invoice.amount_total, 15086.95, places=2)

    def test_custom_rounding_company_globally(self):
        self.company.write({"tax_calculation_rounding_method": "round_globally"})
        self.partner.write({"tax_calculation_rounding_method": "round_per_line"})
        sale_order = self.create_sale_order()
        self.assertEqual(sale_order.tax_calculation_rounding_method, "round_per_line")
        self.assertAlmostEqual(sale_order.amount_total, 15086.95, places=2)
        sale_order.write({"tax_calculation_rounding_method": False})
        self.assertAlmostEqual(sale_order.amount_total, 15086.96, places=2)
        sale_order.write({"tax_calculation_rounding_method": "round_per_line"})
        self.assertAlmostEqual(sale_order.amount_total, 15086.95, places=2)
        sale_order.write({"tax_calculation_rounding_method": "round_globally"})
        self.assertAlmostEqual(sale_order.amount_total, 15086.96, places=2)
        sale_order.write({"tax_calculation_rounding_method": "round_per_line"})
        sale_order.action_confirm()
        invoice = sale_order._create_invoices()
        self.assertEqual(invoice.tax_calculation_rounding_method, "round_per_line")
        self.assertAlmostEqual(invoice.amount_total, 15086.95, places=2)

    def test_custom_rounding_company_per_line(self):
        self.company.write({"tax_calculation_rounding_method": "round_per_line"})
        self.partner.write({"tax_calculation_rounding_method": "round_globally"})
        sale_order = self.create_sale_order()
        self.assertEqual(sale_order.tax_calculation_rounding_method, "round_globally")
        self.assertAlmostEqual(sale_order.amount_total, 15086.96, places=2)
        sale_order.write({"tax_calculation_rounding_method": False})
        self.assertAlmostEqual(sale_order.amount_total, 15086.95, places=2)
        sale_order.write({"tax_calculation_rounding_method": "round_globally"})
        self.assertAlmostEqual(sale_order.amount_total, 15086.96, places=2)
        sale_order.write({"tax_calculation_rounding_method": "round_per_line"})
        self.assertAlmostEqual(sale_order.amount_total, 15086.95, places=2)
        sale_order.write({"tax_calculation_rounding_method": "round_globally"})
        sale_order.action_confirm()
        invoice = sale_order._create_invoices()
        self.assertEqual(invoice.tax_calculation_rounding_method, "round_globally")
        self.assertAlmostEqual(invoice.amount_total, 15086.96, places=2)

    def test_split_invoices(self):
        self.partner.write({"tax_calculation_rounding_method": False})
        sale_order_1 = self.create_sale_order()
        sale_order_2 = self.create_sale_order()
        sale_order_1.write({"tax_calculation_rounding_method": "round_per_line"})
        sale_order_2.write({"tax_calculation_rounding_method": "round_globally"})
        sale_order_1.action_confirm()
        sale_order_2.action_confirm()
        invoices = (sale_order_1 + sale_order_2)._create_invoices()
        self.assertEqual(len(invoices), 2)
        invoice_round_per_line = invoices.filtered(
            lambda a: a.tax_calculation_rounding_method == "round_per_line"
        )
        self.assertAlmostEqual(invoice_round_per_line.amount_total, 15086.95, places=2)
        invoice_round_globally = invoices.filtered(
            lambda a: a.tax_calculation_rounding_method == "round_globally"
        )
        self.assertAlmostEqual(invoice_round_globally.amount_total, 15086.96, places=2)
