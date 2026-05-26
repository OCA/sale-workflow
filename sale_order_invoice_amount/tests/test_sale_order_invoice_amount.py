# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)
from odoo import fields
from odoo.fields import Command, Domain
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestSaleOrderInvoiceAmount(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.write(
            {
                "group_ids": [
                    Command.link(cls.env.ref("sales_team.group_sale_manager").id)
                ]
            }
        )

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
        cls.currency_eur = cls.env.ref("base.EUR")
        cls.currency_eur.active = True
        cls.currency_cad = cls.env.ref("base.CAD")
        cls.currency_cad.active = True
        cls.env["res.currency.rate"].search(
            Domain([("currency_id", "in", [cls.currency_eur.id, cls.currency_cad.id])])
        ).unlink()
        cls.env["res.currency.rate"].create(
            [
                {
                    "name": fields.Date.from_string("2024-01-01"),
                    "rate": 1.500000,  # Fixing the rate for test support.
                    "currency_id": cls.currency_eur.id,
                },
                {
                    "name": fields.Date.from_string("2024-01-01"),
                    "rate": 2.00000,  # Fixing the rate for test support.
                    "currency_id": cls.currency_cad.id,
                },
            ]
        )
        cls.res_partner_2 = cls.env["res.partner"].create({"name": "Partner 12"})
        country = cls.env.company.account_fiscal_country_id
        tax_group = cls.env["account.tax.group"].create(
            {"name": "Test Tax Group", "country_id": country.id}
        )
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Tax 15",
                "type_tax_use": "sale",
                "amount": 21,
                "tax_group_id": tax_group.id,
                "country_id": country.id,
            }
        )
        cls.sale_order_1 = cls.env["sale.order"].create(
            {"partner_id": cls.res_partner_1.id}
        )
        sale_order_line_model = cls.env["sale.order.line"]
        cls.order_line_1 = sale_order_line_model.create(
            {
                "order_id": cls.sale_order_1.id,
                "product_id": cls.product_1.id,
                "product_uom_id": cls.product_1.uom_id.id,
                "product_uom_qty": 10.0,
                "price_unit": 10.0,
                "tax_ids": [Command.set(cls.tax.ids)],
            }
        )
        cls.order_line_2 = sale_order_line_model.create(
            {
                "order_id": cls.sale_order_1.id,
                "product_id": cls.product_2.id,
                "product_uom_id": cls.product_2.uom_id.id,
                "product_uom_qty": 25.0,
                "price_unit": 4.0,
                "tax_ids": [Command.set(cls.tax.ids)],
            }
        )
        cls.order_line_3 = sale_order_line_model.create(
            {
                "order_id": cls.sale_order_1.id,
                "product_id": cls.product_3.id,
                "product_uom_id": cls.product_3.uom_id.id,
                "product_uom_qty": 20.0,
                "price_unit": 5.0,
                "tax_ids": [Command.set(cls.tax.ids)],
            }
        )

    def test_01_sale_order_invoiced_amount(self):
        self.assertEqual(
            self.sale_order_1.amount_invoiced,
            0.0,
            "Invoiced Amount should be 0.0",
        )

        self.sale_order_1.action_confirm()
        aml1 = self.order_line_1._prepare_invoice_line()
        aml2 = self.order_line_2._prepare_invoice_line()
        test_invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "invoice_date": fields.Date.from_string("2024-01-01"),
                "date": fields.Date.from_string("2024-01-01"),
                "partner_id": self.res_partner_1.id,
                "line_ids": [
                    Command.create(
                        aml1,
                    ),
                    Command.create(
                        aml2,
                    ),
                ],
            }
        )
        test_invoice.action_post()
        self.assertEqual(
            self.sale_order_1.amount_invoiced,
            242.0,
            "Invoiced Amount should be 242.0",
        )
        self.assertEqual(
            self.sale_order_1.amount_to_invoice,
            121.0,
            "Uninvoiced Amount should be 121.0, as the lines keep uninvoiced.",
        )
        tax_totals = self.sale_order_1.tax_totals
        self.assertEqual(
            tax_totals["amount_invoiced"],
            242.0,
        )
        self.assertEqual(
            tax_totals["amount_to_invoice"],
            121.00,
        )
        self.assertEqual(
            tax_totals["formatted_amount_invoiced"],
            "$\xa0242.00",
        )
        self.assertEqual(
            tax_totals["formatted_amount_to_invoice"],
            "$\xa0121.00",
        )

    def test_02_sale_order_invoiced_amount_different_currencies_invoice(self):
        self.assertEqual(
            self.sale_order_1.amount_invoiced,
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
            {
                "move_type": "out_invoice",
                "invoice_date": fields.Date.from_string("2024-01-01"),
                "date": fields.Date.from_string("2024-01-01"),
                "partner_id": self.res_partner_1.id,
                "line_ids": [
                    Command.create(
                        aml1,
                    ),
                    Command.create(
                        aml2,
                    ),
                ],
                "currency_id": self.currency_eur.id,
            }
        )
        test_invoice.action_post()
        self.assertAlmostEqual(
            self.sale_order_1.amount_invoiced,
            242.0,
            delta=1,
        )
        self.assertEqual(
            self.sale_order_1.amount_to_invoice,
            121.0,
            "Uninvoiced Amount should be 121, as the lines keep uninvoiced.",
        )

    def test_03_sale_order_invoiced_amount_different_currencies_sale(self):
        self.currency_cad.active = True
        self.sale_order_1 = self.env["sale.order"].create(
            {"partner_id": self.res_partner_1.id, "currency_id": self.currency_eur.id}
        )
        self.order_line_1 = self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order_1.id,
                "product_id": self.product_1.id,
                "product_uom_id": self.product_1.uom_id.id,
                "product_uom_qty": 10.0,
                "price_unit": 10.0,
                "tax_ids": [Command.set(self.tax.ids)],
                "currency_id": self.currency_eur.id,
            }
        )
        self.order_line_2 = self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order_1.id,
                "product_id": self.product_2.id,
                "product_uom_id": self.product_2.uom_id.id,
                "product_uom_qty": 25.0,
                "price_unit": 4.0,
                "tax_ids": [Command.set(self.tax.ids)],
                "currency_id": self.currency_eur.id,
            }
        )
        self.order_line_3 = self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order_1.id,
                "product_id": self.product_3.id,
                "product_uom_id": self.product_3.uom_id.id,
                "product_uom_qty": 20.0,
                "price_unit": 5.0,
                "tax_ids": [Command.set(self.tax.ids)],
                "currency_id": self.currency_eur.id,
            }
        )

        self.assertEqual(
            self.sale_order_1.amount_invoiced,
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
            {
                "move_type": "out_invoice",
                "invoice_date": fields.Date.from_string("2024-01-01"),
                "date": fields.Date.from_string("2024-01-01"),
                "partner_id": self.res_partner_1.id,
                "line_ids": [
                    Command.create(
                        aml1,
                    ),
                    Command.create(
                        aml2,
                    ),
                ],
                "currency_id": self.currency_cad.id,
            }
        )
        test_invoice.action_post()
        self.assertAlmostEqual(self.sale_order_1.amount_invoiced, 242.0, delta=0.2)
        self.assertEqual(
            self.sale_order_1.amount_to_invoice,
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
                    "line_ids": [
                        Command.create(
                            aml1,
                        ),
                        Command.create(
                            aml2,
                        ),
                        Command.create(
                            aml3,
                        ),
                    ],
                    "currency_id": self.currency_cad.id,
                }
            ]
        )
        test_invoice.action_post()
        self.assertAlmostEqual(self.sale_order_1.amount_invoiced, 363.0, delta=0.2)
        self.assertEqual(
            self.sale_order_1.amount_to_invoice,
            0.0,
            "Uninvoiced Amount should be calculated.",
        )

    def test_05_sale_order_invoiced(self):
        self.assertEqual(
            self.sale_order_1.amount_invoiced,
            0.0,
            "Invoiced Amount should be 0.0",
        )

        self.sale_order_1.action_confirm()
        aml1 = self.order_line_1._prepare_invoice_line()
        aml1["price_unit"] = 15.0
        aml1["quantity"] = 5.0
        aml2 = self.order_line_2._prepare_invoice_line()
        test_invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "invoice_date": fields.Date.from_string("2024-01-01"),
                "date": fields.Date.from_string("2024-01-01"),
                "partner_id": self.res_partner_1.id,
                "line_ids": [
                    Command.create(
                        aml1,
                    ),
                    Command.create(
                        aml2,
                    ),
                ],
            }
        )
        test_invoice.action_post()
        self.assertEqual(
            self.sale_order_1.amount_invoiced,
            211.75,
            "Invoiced Amount should be 211.75",
        )
        self.assertEqual(
            self.sale_order_1.amount_to_invoice,
            181.5,
            "Uninvoiced Amount should be 181.5, as the lines keep uninvoiced.",
        )
