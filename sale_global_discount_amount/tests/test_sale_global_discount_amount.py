# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase


class TestSaleGlobalDiscountAmount(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # ==== Partners ====
        partner = cls.env["res.partner"].create({"name": "Partner Test"})

        # ==== Products ====
        product01 = cls.env.ref("product.consu_delivery_01")
        product01.update({"invoice_policy": "order"})
        product02 = cls.env.ref("product.consu_delivery_02")
        product02.update({"invoice_policy": "order"})
        product03 = cls.env.ref("product.consu_delivery_03")
        product03.update({"invoice_policy": "order"})
        cls.discount_product = cls.env.ref(
            "account_global_discount_amount.discount_product"
        )

        # ==== Accounts ====
        type_current_liability = cls.env.ref(
            "account.data_account_type_current_liabilities"
        )
        output_vat10_acct = cls.env["account.account"].create(
            {"name": "10", "code": "10", "user_type_id": type_current_liability.id}
        )
        output_vat20_acct = cls.env["account.account"].create(
            {"name": "20", "code": "20", "user_type_id": type_current_liability.id}
        )

        # ==== Taxes ====
        tax_group_vat10 = cls.env["account.tax.group"].create({"name": "VAT10"})
        tax_group_vat20 = cls.env["account.tax.group"].create({"name": "VAT20"})
        cls.vat10 = cls.env["account.tax"].create(
            {
                "name": "TEST 10%",
                "type_tax_use": "sale",
                "amount_type": "percent",
                "amount": 10.00,
                "tax_group_id": tax_group_vat10.id,
                "invoice_repartition_line_ids": [
                    (0, 0, {"factor_percent": 100.0, "repartition_type": "base"}),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100.0,
                            "repartition_type": "tax",
                            "account_id": output_vat10_acct.id,
                        },
                    ),
                ],
            }
        )
        cls.vat20 = cls.env["account.tax"].create(
            {
                "name": "TEST 20%",
                "type_tax_use": "sale",
                "amount_type": "percent",
                "amount": 20.00,
                "tax_group_id": tax_group_vat20.id,
                "invoice_repartition_line_ids": [
                    (0, 0, {"factor_percent": 100.0, "repartition_type": "base"}),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100.0,
                            "repartition_type": "tax",
                            "account_id": output_vat20_acct.id,
                        },
                    ),
                ],
            }
        )

        # ==== Sale Order with single tax ====
        single_tax_order_line_vals = [
            (
                0,
                0,
                {
                    "product_id": product01.id,
                    "product_uom_qty": 1.0,
                    "name": "Line 1",
                    "price_unit": 200.00,
                    "tax_id": [(6, 0, [cls.vat10.id])],
                },
            )
        ]
        cls.sale_single_tax = cls.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": single_tax_order_line_vals,
                "global_discount_amount": 30.00,
            }
        )

        # ==== Sale Order with 2 lines and 2 different taxes ====
        multi_tax_2_order_line_vals = [
            (
                0,
                0,
                {
                    "product_id": product01.id,
                    "product_uom_qty": 1.0,
                    "name": "Line 1",
                    "price_unit": 200.00,
                    "tax_id": [(6, 0, [cls.vat10.id])],
                },
            ),
            (
                0,
                0,
                {
                    "product_id": product03.id,
                    "product_uom_qty": 1.0,
                    "name": "Line 2",
                    "price_unit": 150.00,
                    "tax_id": [(6, 0, [cls.vat20.id])],
                },
            ),
        ]
        cls.sale_2_lines_multi_tax = cls.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": multi_tax_2_order_line_vals,
                "global_discount_amount": 50.00,
            }
        )

        # ==== Sale Order with 3 lines and 2 different taxes ====
        multi_tax_3_order_line_vals = [
            (
                0,
                0,
                {
                    "product_id": product01.id,
                    "product_uom_qty": 1.0,
                    "name": "Line 1",
                    "price_unit": 200.00,
                    "tax_id": [(6, 0, [cls.vat10.id])],
                },
            ),
            (
                0,
                0,
                {
                    "product_id": product02.id,
                    "product_uom_qty": 1.0,
                    "name": "Line 2",
                    "price_unit": 100.00,
                    "tax_id": [(6, 0, [cls.vat20.id])],
                },
            ),
            (
                0,
                0,
                {
                    "product_id": product03.id,
                    "product_uom_qty": 1.0,
                    "name": "Line 3",
                    "price_unit": 150.00,
                    "tax_id": [(6, 0, [cls.vat20.id])],
                },
            ),
        ]
        cls.sale_3_lines_multi_tax = cls.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": multi_tax_3_order_line_vals,
                "global_discount_amount": 50.00,
            }
        )

    def test_create_sale_single_tax_with_global_discount(self):
        self.assertEqual(self.sale_single_tax.amount_total, 187.00)
        self.assertEqual(self.sale_single_tax.amount_tax, 17.00)
        self.assertEqual(self.sale_single_tax.global_discount_ok, True)
        discount_order_lines = self.env["sale.order.line"].search(
            [
                ("product_id", "=", self.discount_product.id),
                ("order_id", "=", self.sale_single_tax.id),
            ]
        )
        self.assertEqual(len(discount_order_lines), 1)
        self.assertEqual(discount_order_lines[0].is_discount_line, True)
        self.assertEqual(discount_order_lines[0].price_unit, -30.00)
        self.assertEqual(discount_order_lines[0].product_uom_qty, 1.0)
        self.assertEqual(len(discount_order_lines[0].tax_id), 1)
        self.assertEqual(discount_order_lines[0].tax_id[0].name, "TEST 10%")

    def test_duplicate_sale_single_tax_with_global_discount(self):
        copy_sale_single_tax = self.sale_single_tax.copy()
        self.assertEqual(
            self.sale_single_tax.amount_total, copy_sale_single_tax.amount_total
        )
        self.assertEqual(
            self.sale_single_tax.amount_tax, copy_sale_single_tax.amount_tax
        )
        discount_order_lines = self.env["sale.order.line"].search(
            [
                ("product_id", "=", self.discount_product.id),
                ("order_id", "=", copy_sale_single_tax.id),
            ]
        )
        self.assertEqual(len(discount_order_lines), 1)
        self.assertEqual(discount_order_lines[0].is_discount_line, True)
        self.assertEqual(discount_order_lines[0].price_unit, -30.00)
        self.assertEqual(discount_order_lines[0].product_uom_qty, 1.0)
        self.assertEqual(len(discount_order_lines[0].tax_id), 1)
        self.assertEqual(discount_order_lines[0].tax_id[0].name, "TEST 10%")

    def test_create_sale_2_lines_multi_tax_with_global_discount(self):
        self.assertEqual(self.sale_2_lines_multi_tax.amount_untaxed, 300.00)
        self.assertEqual(self.sale_2_lines_multi_tax.amount_tax, 42.85)
        self.assertEqual(self.sale_2_lines_multi_tax.amount_total, 342.85)
        self.assertEqual(self.sale_2_lines_multi_tax.global_discount_ok, True)
        discount_order_lines = self.env["sale.order.line"].search(
            [
                ("product_id", "=", self.discount_product.id),
                ("order_id", "=", self.sale_2_lines_multi_tax.id),
            ]
        )
        self.assertEqual(len(discount_order_lines), 2)
        discount_line_10 = discount_order_lines.filtered(
            lambda x: x.tax_id == self.vat10
        )
        self.assertEqual(discount_line_10.price_unit, -28.57)
        discount_line_20 = discount_order_lines.filtered(
            lambda x: x.tax_id == self.vat20
        )
        self.assertEqual(discount_line_20.price_unit, -21.43)

    def test_duplicate_sale_2_lines_multi_tax_with_global_discount(self):
        copy_sale_2_lines_multi_tax = self.sale_2_lines_multi_tax.copy()
        self.assertEqual(
            self.sale_2_lines_multi_tax.amount_untaxed,
            copy_sale_2_lines_multi_tax.amount_untaxed,
        )
        self.assertEqual(
            self.sale_2_lines_multi_tax.amount_tax,
            copy_sale_2_lines_multi_tax.amount_tax,
        )
        self.assertEqual(
            self.sale_2_lines_multi_tax.amount_total,
            copy_sale_2_lines_multi_tax.amount_total,
        )
        discount_order_lines = self.env["sale.order.line"].search(
            [
                ("product_id", "=", self.discount_product.id),
                ("order_id", "=", copy_sale_2_lines_multi_tax.id),
            ]
        )
        self.assertEqual(len(discount_order_lines), 2)
        discount_line_10 = discount_order_lines.filtered(
            lambda x: x.tax_id == self.vat10
        )
        self.assertEqual(discount_line_10.price_unit, -28.57)
        discount_line_20 = discount_order_lines.filtered(
            lambda x: x.tax_id == self.vat20
        )
        self.assertEqual(discount_line_20.price_unit, -21.43)

    def test_create_sale_3_lines_multi_tax_with_global_discount(self):
        self.assertEqual(self.sale_3_lines_multi_tax.amount_untaxed, 400.00)
        self.assertEqual(self.sale_3_lines_multi_tax.amount_tax, 62.22)
        self.assertEqual(self.sale_3_lines_multi_tax.amount_total, 462.22)
        self.assertEqual(self.sale_3_lines_multi_tax.global_discount_ok, True)
        discount_order_lines = self.env["sale.order.line"].search(
            [
                ("product_id", "=", self.discount_product.id),
                ("order_id", "=", self.sale_3_lines_multi_tax.id),
            ]
        )
        self.assertEqual(len(discount_order_lines), 2)
        discount_line_10 = discount_order_lines.filtered(
            lambda x: x.tax_id == self.vat10
        )
        self.assertEqual(discount_line_10.price_unit, -22.22)
        discount_line_20 = discount_order_lines.filtered(
            lambda x: x.tax_id == self.vat20
        )
        self.assertEqual(discount_line_20.price_unit, -27.78)

    def test_duplicate_sale_3_lines_multi_tax_with_global_discount(self):
        copy_sale_3_lines_multi_tax = self.sale_3_lines_multi_tax.copy()
        self.assertEqual(
            self.sale_3_lines_multi_tax.amount_untaxed,
            copy_sale_3_lines_multi_tax.amount_untaxed,
        )
        self.assertEqual(
            self.sale_3_lines_multi_tax.amount_tax,
            copy_sale_3_lines_multi_tax.amount_tax,
        )
        self.assertEqual(
            self.sale_3_lines_multi_tax.amount_total,
            copy_sale_3_lines_multi_tax.amount_total,
        )
        discount_order_lines = self.env["sale.order.line"].search(
            [
                ("product_id", "=", self.discount_product.id),
                ("order_id", "=", copy_sale_3_lines_multi_tax.id),
            ]
        )
        self.assertEqual(len(discount_order_lines), 2)
        discount_line_10 = discount_order_lines.filtered(
            lambda x: x.tax_id == self.vat10
        )
        self.assertEqual(discount_line_10.price_unit, -22.22)
        discount_line_20 = discount_order_lines.filtered(
            lambda x: x.tax_id == self.vat20
        )
        self.assertEqual(discount_line_20.price_unit, -27.78)

    def test_write_sale_single_tax_with_change_global_discount(self):
        self.sale_single_tax.write({"global_discount_amount": 25.00})
        self.assertEqual(self.sale_single_tax.amount_total, 192.50)
        self.assertEqual(self.sale_single_tax.amount_tax, 17.50)
        self.assertEqual(self.sale_single_tax.global_discount_ok, True)
        discount_order_lines = self.env["sale.order.line"].search(
            [
                ("product_id", "=", self.discount_product.id),
                ("order_id", "=", self.sale_single_tax.id),
            ]
        )
        self.assertEqual(len(discount_order_lines), 1)
        self.assertEqual(discount_order_lines[0].is_discount_line, True)
        self.assertEqual(discount_order_lines[0].price_unit, -25.00)

    def test_write_sale_2_lines_multi_tax_with_change_global_discount(self):
        self.sale_2_lines_multi_tax.write({"global_discount_amount": 45.00})
        self.assertEqual(self.sale_2_lines_multi_tax.amount_untaxed, 305.00)
        self.assertEqual(self.sale_2_lines_multi_tax.amount_tax, 43.57)
        self.assertEqual(self.sale_2_lines_multi_tax.amount_total, 348.57)
        self.assertEqual(self.sale_2_lines_multi_tax.global_discount_ok, True)
        discount_order_lines = self.env["sale.order.line"].search(
            [
                ("product_id", "=", self.discount_product.id),
                ("order_id", "=", self.sale_2_lines_multi_tax.id),
            ]
        )
        self.assertEqual(len(discount_order_lines), 2)
        discount_line_10 = discount_order_lines.filtered(
            lambda x: x.tax_id == self.vat10
        )
        self.assertEqual(discount_line_10.price_unit, -25.71)
        discount_line_20 = discount_order_lines.filtered(
            lambda x: x.tax_id == self.vat20
        )
        self.assertEqual(discount_line_20.price_unit, -19.29)

    def test_write_sale_3_lines_multi_tax_with_change_global_discount(self):
        self.sale_3_lines_multi_tax.write({"global_discount_amount": 45.00})
        self.assertEqual(self.sale_3_lines_multi_tax.amount_untaxed, 405.00)
        self.assertEqual(self.sale_3_lines_multi_tax.amount_tax, 63.00)
        self.assertEqual(self.sale_3_lines_multi_tax.amount_total, 468.00)
        self.assertEqual(self.sale_3_lines_multi_tax.global_discount_ok, True)
        discount_order_lines = self.env["sale.order.line"].search(
            [
                ("product_id", "=", self.discount_product.id),
                ("order_id", "=", self.sale_3_lines_multi_tax.id),
            ]
        )
        self.assertEqual(len(discount_order_lines), 2)
        discount_line_10 = discount_order_lines.filtered(
            lambda x: x.tax_id == self.vat10
        )
        self.assertEqual(discount_line_10.price_unit, -20.00)
        discount_line_20 = discount_order_lines.filtered(
            lambda x: x.tax_id == self.vat20
        )
        self.assertEqual(discount_line_20.price_unit, -25.00)

    def test_write_sale_single_tax_with_null_global_discount(self):
        self.sale_single_tax.write({"global_discount_amount": 0.00})
        self.assertEqual(self.sale_single_tax.amount_total, 220.00)
        self.assertEqual(self.sale_single_tax.amount_tax, 20.00)
        self.assertEqual(self.sale_single_tax.global_discount_ok, True)
        discount_order_lines = self.env["sale.order.line"].search(
            [
                ("product_id", "=", self.discount_product.id),
                ("order_id", "=", self.sale_single_tax.id),
            ]
        )
        self.assertEqual(len(discount_order_lines), 0)

    def test_write_sale_2_lines_multi_tax_with_null_global_discount(self):
        self.sale_2_lines_multi_tax.write({"global_discount_amount": 0.00})
        self.assertEqual(self.sale_2_lines_multi_tax.amount_untaxed, 350.00)
        self.assertEqual(self.sale_2_lines_multi_tax.amount_tax, 50.00)
        self.assertEqual(self.sale_2_lines_multi_tax.amount_total, 400.00)
        self.assertEqual(self.sale_2_lines_multi_tax.global_discount_ok, True)
        discount_order_lines = self.env["sale.order.line"].search(
            [
                ("product_id", "=", self.discount_product.id),
                ("order_id", "=", self.sale_2_lines_multi_tax.id),
            ]
        )
        self.assertEqual(len(discount_order_lines), 0)

    def test_write_sale_3_lines_multi_tax_with_null_global_discount(self):
        self.sale_3_lines_multi_tax.write({"global_discount_amount": 0.00})
        self.assertEqual(self.sale_3_lines_multi_tax.amount_untaxed, 450.00)
        self.assertEqual(self.sale_3_lines_multi_tax.amount_tax, 70.00)
        self.assertEqual(self.sale_3_lines_multi_tax.amount_total, 520.00)
        self.assertEqual(self.sale_3_lines_multi_tax.global_discount_ok, True)
        discount_order_lines = self.env["sale.order.line"].search(
            [
                ("product_id", "=", self.discount_product.id),
                ("order_id", "=", self.sale_3_lines_multi_tax.id),
            ]
        )
        self.assertEqual(len(discount_order_lines), 0)

    def test_create_invoice_from_sale_single_tax_with_global_discount(self):
        self.sale_single_tax.action_confirm()
        self.context = {
            "active_model": "sale.order",
            "active_ids": [self.sale_single_tax.id],
            "active_id": self.sale_single_tax.id,
        }
        payment = (
            self.env["sale.advance.payment.inv"]
            .with_context(self.context)
            .create({"advance_payment_method": "delivered"})
        )
        payment.create_invoices()
        invoices = self.sale_single_tax.invoice_ids
        self.assertEqual(len(invoices), 1)

        self.assertEqual(invoices[0].amount_total, 187.00)
        self.assertEqual(invoices[0].amount_tax, 17.00)
        self.assertEqual(invoices[0].global_discount_ok, True)
        discount_move_lines = self.env["account.move.line"].search(
            [
                ("product_id", "=", self.discount_product.id),
                ("move_id", "=", invoices[0].id),
            ]
        )
        self.assertEqual(len(discount_move_lines), 1)
        self.assertEqual(discount_move_lines[0].is_discount_line, True)
        self.assertEqual(discount_move_lines[0].price_unit, -30.00)
        self.assertEqual(discount_move_lines[0].quantity, 1.0)
        self.assertEqual(len(discount_move_lines[0].tax_ids), 1)
        self.assertEqual(discount_move_lines[0].tax_ids[0].name, "TEST 10%")

    def test_create_invoice_from_sale_2_lines_multi_tax_with_global_discount(self):
        self.sale_2_lines_multi_tax.action_confirm()
        self.context = {
            "active_model": "sale.order",
            "active_ids": [self.sale_2_lines_multi_tax.id],
            "active_id": self.sale_2_lines_multi_tax.id,
        }
        payment = (
            self.env["sale.advance.payment.inv"]
            .with_context(self.context)
            .create({"advance_payment_method": "delivered"})
        )
        payment.create_invoices()
        invoices = self.sale_2_lines_multi_tax.invoice_ids
        self.assertEqual(len(invoices), 1)

        self.assertEqual(invoices[0].amount_untaxed, 300.00)
        self.assertEqual(invoices[0].amount_tax, 42.85)
        self.assertEqual(invoices[0].amount_total, 342.85)
        self.assertEqual(invoices[0].global_discount_ok, True)
        discount_move_lines = self.env["account.move.line"].search(
            [
                ("product_id", "=", self.discount_product.id),
                ("move_id", "=", invoices[0].id),
            ]
        )
        self.assertEqual(len(discount_move_lines), 2)
        discount_line_10 = discount_move_lines.filtered(
            lambda x: x.tax_ids == self.vat10
        )
        self.assertEqual(discount_line_10.price_unit, -28.57)
        discount_line_20 = discount_move_lines.filtered(
            lambda x: x.tax_ids == self.vat20
        )
        self.assertEqual(discount_line_20.price_unit, -21.43)

    def test_create_invoice_from_sale_3_lines_multi_tax_with_global_discount(self):
        self.sale_3_lines_multi_tax.action_confirm()
        self.context = {
            "active_model": "sale.order",
            "active_ids": [self.sale_3_lines_multi_tax.id],
            "active_id": self.sale_3_lines_multi_tax.id,
        }
        payment = (
            self.env["sale.advance.payment.inv"]
            .with_context(self.context)
            .create({"advance_payment_method": "delivered"})
        )
        payment.create_invoices()
        invoices = self.sale_3_lines_multi_tax.invoice_ids
        self.assertEqual(len(invoices), 1)

        self.assertEqual(invoices[0].amount_untaxed, 400.00)
        self.assertEqual(invoices[0].amount_tax, 62.22)
        self.assertEqual(invoices[0].amount_total, 462.22)
        self.assertEqual(invoices[0].global_discount_ok, True)
        discount_move_lines = self.env["account.move.line"].search(
            [
                ("product_id", "=", self.discount_product.id),
                ("move_id", "=", invoices[0].id),
            ]
        )
        self.assertEqual(len(discount_move_lines), 2)
        discount_line_10 = discount_move_lines.filtered(
            lambda x: x.tax_ids == self.vat10
        )
        self.assertEqual(discount_line_10.price_unit, -22.22)
        discount_line_20 = discount_move_lines.filtered(
            lambda x: x.tax_ids == self.vat20
        )
        self.assertEqual(discount_line_20.price_unit, -27.78)
