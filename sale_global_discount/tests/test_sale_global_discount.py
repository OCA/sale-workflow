# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import exceptions
from odoo.tests import common


class TestSaleGlobalDiscount(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.account_type = cls.env["account.account.type"].create(
            {"name": "Test", "type": "receivable"}
        )
        cls.account = cls.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TEST",
                "user_type_id": cls.account_type.id,
                "reconcile": True,
            }
        )
        cls.global_discount_obj = cls.env["global.discount"]
        cls.global_discount_1 = cls.global_discount_obj.create(
            {
                "name": "Test Discount 1",
                "sequence": 1,
                "discount_scope": "sale",
                "discount": 20,
                "account_id": cls.account.id,
            }
        )
        cls.global_discount_2 = cls.global_discount_obj.create(
            {
                "name": "Test Discount 2",
                "sequence": 2,
                "discount_scope": "sale",
                "discount": 30,
                "account_id": cls.account.id,
            }
        )
        cls.global_discount_3 = cls.global_discount_obj.create(
            {
                "name": "Test Discount 3",
                "sequence": 3,
                "discount_scope": "sale",
                "discount": 50,
                "account_id": cls.account.id,
            }
        )
        cls.partner_1 = cls.env["res.partner"].create({"name": "Mr. Odoo"})
        cls.partner_2 = cls.env["res.partner"].create({"name": "Mrs. Odoo"})
        cls.partner_2.customer_global_discount_ids = (
            cls.global_discount_2 + cls.global_discount_3
        )
        cls.product_1 = cls.env["product.product"].create(
            {"name": "Test Product 1", "type": "service"}
        )
        cls.product_2 = cls.product_1.copy({"name": "Test Product 2"})
        cls.tax_group_5pc = cls.env["account.tax.group"].create(
            {"name": "Test Tax Group 5%", "sequence": 1}
        )
        cls.tax_group_15pc = cls.env["account.tax.group"].create(
            {"name": "Test Tax Group 15%", "sequence": 2}
        )
        cls.tax_1 = cls.env["account.tax"].create(
            {
                "name": "Test TAX 15%",
                "amount_type": "percent",
                "type_tax_use": "sale",
                "tax_group_id": cls.tax_group_15pc.id,
                "amount": 15.0,
            }
        )
        cls.tax_2 = cls.env["account.tax"].create(
            {
                "name": "TAX 5%",
                "amount_type": "percent",
                "tax_group_id": cls.tax_group_5pc.id,
                "type_tax_use": "sale",
                "amount": 5.0,
            }
        )
        cls.sale = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_1.id,
                            "product_uom_qty": 2,
                            "price_unit": 75.00,
                            # Test compound taxes as they tend to provoke corner cases
                            "tax_id": [(6, 0, [cls.tax_1.id, cls.tax_2.id])],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "On Site Assistance",
                            "product_id": cls.product_2.id,
                            "product_uom_qty": 3,
                            "price_unit": 33.33,
                            "tax_id": [(6, 0, [cls.tax_1.id, cls.tax_2.id])],
                        },
                    ),
                ],
            }
        )

    def test_01_global_sale_succesive_discounts(self):
        """Add global discounts to the sale order"""
        self.assertAlmostEqual(self.sale.amount_total, 299.99)
        self.assertAlmostEqual(self.sale.amount_tax, 50)
        self.assertAlmostEqual(self.sale.amount_untaxed, 249.99)
        # Apply a single 20% global discount
        self.sale.global_discount_ids = self.global_discount_1
        # Discount is computed over the base and global taxes are computed
        # according to it line by line with the core method
        self.assertAlmostEqual(self.sale.amount_global_discount, 50)
        self.assertAlmostEqual(self.sale.amount_untaxed, 199.99)
        self.assertAlmostEqual(self.sale.amount_untaxed_before_global_discounts, 249.99)
        self.assertAlmostEqual(self.sale.amount_total, 239.99)
        self.assertAlmostEqual(self.sale.amount_total_before_global_discounts, 299.99)
        self.assertAlmostEqual(self.sale.amount_tax, 40)
        # Apply an additional 30% global discount
        self.sale.global_discount_ids += self.global_discount_2
        self.assertAlmostEqual(self.sale.amount_global_discount, 110)
        self.assertAlmostEqual(self.sale.amount_untaxed, 139.99)
        self.assertAlmostEqual(self.sale.amount_untaxed_before_global_discounts, 249.99)
        self.assertAlmostEqual(self.sale.amount_total, 167.99)
        self.assertAlmostEqual(self.sale.amount_total_before_global_discounts, 299.99)
        self.assertAlmostEqual(self.sale.amount_tax, 28)

    def test_02_global_sale_discounts_from_partner(self):
        """Change the partner and his global discounts go to the invoice"""
        # (30% then 50%)
        self.sale.partner_id = self.partner_2
        self.sale.onchange_partner_id()
        self.assertAlmostEqual(self.sale.amount_global_discount, 162.49)
        self.assertAlmostEqual(self.sale.amount_untaxed, 87.5)
        self.assertAlmostEqual(self.sale.amount_untaxed_before_global_discounts, 249.99)
        self.assertAlmostEqual(self.sale.amount_total, 105.01)
        self.assertAlmostEqual(self.sale.amount_total_before_global_discounts, 299.99)
        self.assertAlmostEqual(self.sale.amount_tax, 17.51)

    def test_03_global_sale_discounts_to_invoice(self):
        """All the discounts go to the invoice"""
        self.sale.partner_id = self.partner_2
        self.sale.onchange_partner_id()
        self.sale.action_confirm()
        self.sale.action_invoice_create()
        invoice = self.sale.invoice_ids
        self.assertEqual(len(invoice.invoice_global_discount_ids), 2)
        line_tax_1 = invoice.tax_line_ids.filtered(lambda x: x.tax_id == self.tax_1)
        line_tax_2 = invoice.tax_line_ids.filtered(lambda x: x.tax_id == self.tax_2)
        self.assertAlmostEqual(line_tax_1.base, 87.5)
        self.assertAlmostEqual(line_tax_2.base, 87.5)
        self.assertAlmostEqual(line_tax_1.amount, 13.13)
        self.assertAlmostEqual(line_tax_2.amount, 4.38)
        discount_amount = sum(
            invoice.invoice_global_discount_ids.mapped("discount_amount")
        )
        self.assertAlmostEqual(discount_amount, 162.49)
        self.assertAlmostEqual(invoice.amount_untaxed_before_global_discounts, 249.99)
        self.assertAlmostEqual(invoice.amount_untaxed, 87.5)
        self.assertAlmostEqual(invoice.amount_total, 105.01)

    def test_04_report_taxes(self):
        """Taxes by group shown in reports"""
        self.sale.partner_id = self.partner_2
        self.sale.onchange_partner_id()
        self.sale._amount_by_group()
        # Taxes
        taxes_groups = self.sale.amount_by_group
        self.assertAlmostEqual(taxes_groups[0][1], 4.38)
        self.assertAlmostEqual(taxes_groups[1][1], 13.13)
        # Bases
        self.assertAlmostEqual(taxes_groups[0][2], 87.5)
        self.assertAlmostEqual(taxes_groups[1][2], 87.5)

    def test_05_incompatible_taxes(self):
        # Line 1 with tax 1 and tax 2
        # Line 2 with only tax 2
        self.sale.order_line[1].tax_id = [(6, 0, self.tax_1.ids)]
        with self.assertRaises(exceptions.UserError):
            self.sale.global_discount_ids = self.global_discount_1

    def test_06_no_taxes(self):
        self.sale.order_line[1].tax_id = False
        with self.assertRaises(exceptions.UserError):
            self.sale.global_discount_ids = self.global_discount_1
