# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import fields
from odoo.tests import common


class TestSaleOrderInvoiceAmount(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Partners
        cls.res_partner_1 = cls.env["res.partner"].create({"name": "Wood Corner"})
        cls.res_partner_address_1 = cls.env["res.partner"].create(
            {"name": "Willie Burke", "parent_id": cls.res_partner_1.id}
        )
        cls.currency_eur = cls.env.ref("base.EUR")
        cls.currency_cad = cls.env.ref("base.CAD")
        cls.res_partner_2 = cls.env["res.partner"].create({"name": "Partner 12"})

        # Products
        cls.product_1 = cls.env["product.product"].create(
            {"name": "Desk Combination", "type": "product", "invoice_policy": "order"}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Conference Chair", "type": "product", "invoice_policy": "order"}
        )
        cls.product_3 = cls.env["product.product"].create(
            {"name": "Repair Services", "type": "service", "invoice_policy": "order"}
        )

        # Location
        cls.stock_warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.stock_location_14 = cls.env["stock.location"].create(
            {"name": "Shelf 2", "location_id": cls.stock_warehouse.lot_stock_id.id}
        )
        # Replenish products
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_1, cls.stock_location_14, 10
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_2, cls.stock_location_14, 10
        )
        # Sale Order
        cls.tax = cls.env["account.tax"].create(
            {"name": "Tax 15", "type_tax_use": "sale", "amount": 21}
        )
        cls.sale_order_1 = cls.env["sale.order"].create(
            {"partner_id": cls.res_partner_1.id}
        )
        cls.order_line_1 = cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order_1.id,
                "product_id": cls.product_1.id,
                "product_uom": cls.product_1.uom_id.id,
                "product_uom_qty": 10.0,
                "price_unit": 10.0,
                "tax_id": cls.tax,
            }
        )
        cls.order_line_2 = cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order_1.id,
                "product_id": cls.product_2.id,
                "product_uom": cls.product_2.uom_id.id,
                "product_uom_qty": 25.0,
                "price_unit": 4.0,
                "tax_id": cls.tax,
            }
        )
        cls.order_line_3 = cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order_1.id,
                "product_id": cls.product_3.id,
                "product_uom": cls.product_3.uom_id.id,
                "product_uom_qty": 20.0,
                "price_unit": 5.0,
                "tax_id": cls.tax,
            }
        )

    def test_01_sale_order_invoiced_amount(self):

        self.assertEqual(
            self.sale_order_1.invoiced_amount,
            0.0,
            "Invoiced Amount should be 0.0",
        )
        self.sale_order_1.action_confirm()
        aml1 = self.order_line_1._prepare_invoice_line()
        aml2 = self.order_line_2._prepare_invoice_line()
        test_invoice = self.env["account.move"].create(
            [
                {
                    "move_type": "out_invoice",
                    "invoice_date": fields.Date.from_string("2024-01-01"),
                    "date": fields.Date.from_string("2024-01-01"),
                    "partner_id": self.res_partner_1.id,
                    "invoice_line_ids": [aml1, aml2],
                }
            ]
        )
        test_invoice.action_post()
        self.assertEqual(
            self.sale_order_1.invoiced_amount,
            242.0,
            "Invoiced Amount should be 242",
        )
        self.assertEqual(
            self.sale_order_1.uninvoiced_amount,
            121.0,
            "Uninvoiced Amount should be 121, as the lines keep uninvoiced.",
        )
        test_invoice.button_cancel()
        self.sale_order_1._create_invoices(final=True)
        self.assertEqual(
            self.sale_order_1.invoiced_amount,
            363.0,
            "Invoiced Amount should be calculated.",
        )
        self.assertEqual(
            self.sale_order_1.uninvoiced_amount,
            0.0,
            "Uninvoiced Amount should be calculated.",
        )

    def test_02_sale_order_invoiced_amount_different_currencies_invoice(self):

        self.assertEqual(
            self.sale_order_1.invoiced_amount,
            0.0,
            "Invoiced Amount should be 0.0",
        )
        self.sale_order_1.action_confirm()
        price_foreign_currency_1 = self.sale_order_1.currency_id._convert(
            10.0,
            self.currency_eur,
            self.sale_order_1.company_id,
            fields.Date.from_string("2024-01-01"),
        )
        price_foreign_currency_2 = self.sale_order_1.currency_id._convert(
            4.0,
            self.currency_eur,
            self.sale_order_1.company_id,
            fields.Date.from_string("2024-01-01"),
        )
        aml1 = self.order_line_1._prepare_invoice_line(
            **{
                "price_unit": price_foreign_currency_1,
                "currency_id": self.currency_eur.id,
            }
        )
        aml2 = self.order_line_2._prepare_invoice_line(
            **{
                "price_unit": price_foreign_currency_2,
                "currency_id": self.currency_eur.id,
            }
        )
        test_invoice = self.env["account.move"].create(
            [
                {
                    "move_type": "out_invoice",
                    "invoice_date": fields.Date.from_string("2024-01-01"),
                    "date": fields.Date.from_string("2024-01-01"),
                    "partner_id": self.res_partner_1.id,
                    "invoice_line_ids": [aml1, aml2],
                    "currency_id": self.currency_eur.id,
                }
            ]
        )
        test_invoice.action_post()
        self.assertAlmostEqual(
            self.sale_order_1.invoiced_amount,
            242.0,
            delta=1,
        )
        self.assertEqual(
            self.sale_order_1.uninvoiced_amount,
            121.0,
            "Uninvoiced Amount should be 121, as the lines keep uninvoiced.",
        )
        test_invoice.button_cancel()
        self.sale_order_1._create_invoices(final=True)
        self.assertEqual(
            self.sale_order_1.invoiced_amount,
            363.0,
            "Invoiced Amount should be calculated.",
        )
        self.assertEqual(
            self.sale_order_1.uninvoiced_amount,
            0.0,
            "Uninvoiced Amount should be calculated.",
        )

    def test_03_sale_order_invoiced_amount_different_currencies_sale(self):

        self.sale_order_1 = self.env["sale.order"].create(
            {"partner_id": self.res_partner_1.id, "currency_id": self.currency_eur.id}
        )
        self.order_line_1 = self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order_1.id,
                "product_id": self.product_1.id,
                "product_uom": self.product_1.uom_id.id,
                "product_uom_qty": 10.0,
                "price_unit": 10.0,
                "tax_id": self.tax,
                "currency_id": self.currency_eur.id,
            }
        )
        self.order_line_2 = self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order_1.id,
                "product_id": self.product_2.id,
                "product_uom": self.product_2.uom_id.id,
                "product_uom_qty": 25.0,
                "price_unit": 4.0,
                "tax_id": self.tax,
                "currency_id": self.currency_eur.id,
            }
        )
        self.order_line_3 = self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order_1.id,
                "product_id": self.product_3.id,
                "product_uom": self.product_3.uom_id.id,
                "product_uom_qty": 20.0,
                "price_unit": 5.0,
                "tax_id": self.tax,
                "currency_id": self.currency_eur.id,
            }
        )

        self.assertEqual(
            self.sale_order_1.invoiced_amount,
            0.0,
            "Invoiced Amount should be 0.0",
        )
        self.sale_order_1.action_confirm()
        self.sale_order_1.currency_id = self.currency_eur
        price_foreign_currency_1 = self.sale_order_1.currency_id._convert(
            10.0,
            self.currency_cad,
            self.sale_order_1.company_id,
            fields.Date.from_string("2024-01-01"),
        )
        price_foreign_currency_2 = self.sale_order_1.currency_id._convert(
            4.0,
            self.currency_cad,
            self.sale_order_1.company_id,
            fields.Date.from_string("2024-01-01"),
        )
        aml1 = self.order_line_1._prepare_invoice_line(
            **{
                "price_unit": price_foreign_currency_1,
                "currency_id": self.currency_cad.id,
            }
        )
        aml2 = self.order_line_2._prepare_invoice_line(
            **{
                "price_unit": price_foreign_currency_2,
                "currency_id": self.currency_cad.id,
            }
        )
        test_invoice = self.env["account.move"].create(
            [
                {
                    "move_type": "out_invoice",
                    "invoice_date": fields.Date.from_string("2024-01-01"),
                    "date": fields.Date.from_string("2024-01-01"),
                    "partner_id": self.res_partner_1.id,
                    "invoice_line_ids": [aml1, aml2],
                    "currency_id": self.currency_cad.id,
                }
            ]
        )
        test_invoice.action_post()
        self.assertAlmostEqual(
            self.sale_order_1.invoiced_amount,
            242.0,
            delta=10,
        )
        self.assertEqual(
            self.sale_order_1.uninvoiced_amount,
            121.0,
            "Uninvoiced Amount should be 121, as the lines keep uninvoiced.",
        )
        test_invoice.button_cancel()
        price_foreign_currency_1 = self.sale_order_1.currency_id._convert(
            10.0,
            self.currency_cad,
            self.sale_order_1.company_id,
            fields.Date.from_string("2024-01-01"),
        )
        price_foreign_currency_2 = self.sale_order_1.currency_id._convert(
            4.0,
            self.currency_cad,
            self.sale_order_1.company_id,
            fields.Date.from_string("2024-01-01"),
        )
        price_foreign_currency_3 = self.sale_order_1.currency_id._convert(
            5.0,
            self.currency_cad,
            self.sale_order_1.company_id,
            fields.Date.from_string("2024-01-01"),
        )
        aml1 = self.order_line_1._prepare_invoice_line(
            **{
                "price_unit": price_foreign_currency_1,
                "currency_id": self.currency_cad.id,
            }
        )
        aml2 = self.order_line_2._prepare_invoice_line(
            **{
                "price_unit": price_foreign_currency_2,
                "currency_id": self.currency_cad.id,
            }
        )
        aml3 = self.order_line_3._prepare_invoice_line(
            **{
                "price_unit": price_foreign_currency_3,
                "currency_id": self.currency_cad.id,
            }
        )
        test_invoice = self.env["account.move"].create(
            [
                {
                    "move_type": "out_invoice",
                    "invoice_date": fields.Date.from_string("2024-01-01"),
                    "date": fields.Date.from_string("2024-01-01"),
                    "partner_id": self.res_partner_1.id,
                    "invoice_line_ids": [aml1, aml2, aml3],
                    "currency_id": self.currency_cad.id,
                }
            ]
        )
        test_invoice.action_post()
        self.assertAlmostEqual(
            self.sale_order_1.invoiced_amount,
            363.0,
            delta=15,
        )
        self.assertEqual(
            self.sale_order_1.uninvoiced_amount,
            0.0,
            "Uninvoiced Amount should be calculated.",
        )
