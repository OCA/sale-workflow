# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo.tests import common


class TestSaleOrderInvoiceAmount(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Partners
        partner_model = cls.env["res.partner"]
        cls.res_partner_1 = partner_model.create({"name": "Wood Corner"})
        cls.res_partner_address_1 = partner_model.create(
            {"name": "Willie Burke", "parent_id": cls.res_partner_1.id}
        )
        cls.res_partner_2 = partner_model.create({"name": "Partner 12"})
        # Products
        product_model = cls.env["product.product"]
        cls.product_1 = product_model.create(
            {"name": "Desk Combination", "type": "consu"}
        )
        cls.product_2 = product_model.create(
            {"name": "Conference Chair", "type": "consu"}
        )
        cls.product_3 = product_model.create(
            {"name": "Repair Services", "type": "service"}
        )
        # Sale Order
        cls.tax = cls.env["account.tax"].create(
            {"name": "Tax 15", "type_tax_use": "sale", "amount": 21}
        )
        cls.sale_order_1 = cls.env["sale.order"].create(
            {"partner_id": cls.res_partner_1.id}
        )
        sale_order_line_model = cls.env["sale.order.line"]
        cls.order_line_1 = sale_order_line_model.create(
            {
                "order_id": cls.sale_order_1.id,
                "product_id": cls.product_1.id,
                "product_uom": cls.product_1.uom_id.id,
                "product_uom_qty": 10.0,
                "price_unit": 10.0,
                "tax_id": cls.tax,
            }
        )
        cls.order_line_2 = sale_order_line_model.create(
            {
                "order_id": cls.sale_order_1.id,
                "product_id": cls.product_2.id,
                "product_uom": cls.product_2.uom_id.id,
                "product_uom_qty": 25.0,
                "price_unit": 4.0,
                "tax_id": cls.tax,
            }
        )
        cls.order_line_3 = sale_order_line_model.create(
            {
                "order_id": cls.sale_order_1.id,
                "product_id": cls.product_3.id,
                "product_uom": cls.product_3.uom_id.id,
                "product_uom_qty": 20.0,
                "price_unit": 5.0,
                "tax_id": cls.tax,
            }
        )

    def test_sale_order_invoiced_amount(self):
        self.assertEqual(
            self.sale_order_1.invoiced_amount,
            0.0,
            "Invoiced Amount should be 0.0",
        )
        context_payment = {
            "active_ids": [self.sale_order_1.id],
            "active_id": self.sale_order_1.id,
        }
        payment = (
            self.env["sale.advance.payment.inv"]
            .with_context(**context_payment)
            .create({"advance_payment_method": "fixed", "fixed_amount": 100})
        )

        payment.create_invoices()
        self.assertEqual(
            self.sale_order_1.invoiced_amount,
            100.0,
            "Invoiced Amount should be 100",
        )
        self.assertEqual(
            self.sale_order_1.uninvoiced_amount,
            263.0,
            "Uninvoiced Amount should be 263",
        )

        self.sale_order_1.action_confirm()
        self.sale_order_1._create_invoices(final=True)
        self.assertEqual(
            self.sale_order_1.invoiced_amount,
            363.0,
            "Invoiced Amount should be calculated",
        )
        tax_totals = self.sale_order_1.tax_totals
        self.assertEqual(
            tax_totals["invoiced_amount"],
            363.0,
        )
        self.assertEqual(
            tax_totals["uninvoiced_amount"],
            0.0,
        )
        self.assertEqual(
            tax_totals["formatted_invoiced_amount"],
            "$\xa0363.00",
        )
        self.assertEqual(
            tax_totals["formatted_uninvoiced_amount"],
            "$\xa00.00",
        )
