# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.account_global_discount_amount.tests.common import (
    CommonCaseGlobalDiscount,
    CommonGlobalDiscount,
)


class TestSaleGlobalDiscountAmount(CommonGlobalDiscount, CommonCaseGlobalDiscount):
    @classmethod
    def _create_record(cls, lines, discount_amount):
        # lines should be in the format [(price_unit, qty, tax, discount)]
        order_lines = [
            (
                0,
                0,
                {
                    "product_id": cls.product.id,
                    "price_unit": price,
                    "product_uom_qty": qty,
                    "tax_id": [(6, 0, tax.ids)],
                    "discount": discount_percent,
                },
            )
            for price, qty, tax, discount_percent in lines
        ]
        return cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": order_lines,
                "global_discount_amount": discount_amount,
            }
        )

    def _check_discount_line(self, record, expected):
        lines = [
            (line.tax_id, line.price_unit)
            for line in record.order_line
            if line.is_discount_line
        ]
        lines.sort(key=lambda s: s[0].id)
        expected.sort(key=lambda s: s[0].id)
        self.assertEqual(lines, expected)
        self.assertTrue(record.global_discount_ok)

    def _invoice_sale(self, sale):
        sale.action_confirm()
        wizard = (
            self.env["sale.advance.payment.inv"]
            .with_context(
                {
                    "active_model": "sale.order",
                    "active_ids": sale.ids,
                    "active_id": sale.id,
                }
            )
            .create({"advance_payment_method": "delivered"})
        )
        wizard.create_invoices()
        return sale.invoice_ids

    def test_create_invoice_with_global_discount(self):
        lines = [
            # price, qty, vat, discount
            (10, 3, self.vat20, 0),
            (10, 1, self.vat10, 0),
        ]
        sale = self._create_record(lines, 10)
        invoice = self._invoice_sale(sale)
        self.assertEqual(len(invoice), 1)

        self._check_invoice_discount_line(
            invoice,
            [
                (self.vat20, -7.5),
                (self.vat10, -2.5),
            ],
        )

        self.assertEqual(invoice.global_discount_base_on, "tax_exc")
        self.assertEqual(invoice.amount_untaxed, 30)
        self.assertEqual(invoice.amount_total, 35.25)
        self.assertTrue(invoice.global_discount_ok)
        self.assertEqual(sale.invoice_status, "invoiced")

    def test_partial_invoice_with_global_discount(self):
        lines = [
            # price, qty, vat, discount
            (10, 3, self.vat20, 0),
            (10, 1, self.vat10, 0),
        ]
        sale = self._create_record(lines, 10)
        invoice = self._invoice_sale(sale)
        # we remove a line in the invoice and change the discount
        invoice.write(
            {
                "invoice_line_ids": [(2, invoice.invoice_line_ids[1].id, 0)],
                "global_discount_amount": 7.5,
            }
        )

        invoices = self._invoice_sale(sale)
        invoice_2 = invoices - invoice
        self.assertEqual(invoice_2.global_discount_amount, 2.5)

    def test_create_confirm_and_remove_product(self):
        lines = [
            # price, qty, vat, discount
            (10, 3, self.vat20, 0),
            (10, 1, self.vat10, 0),
        ]
        sale = self._create_record(lines, 10)
        sale.action_confirm()
        sale.order_line[1].product_uom_qty = 0
        self._check_discount_line(
            sale,
            [
                (self.vat20, -10),
            ],
        )
