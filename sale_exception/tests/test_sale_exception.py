# Copyright 2011 Akretion, Sodexis
# Copyright 2018 Akretion
# Copyright 2019 Camptocamp SA
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form, TransactionCase


class TestSaleException(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.default_pl = cls.env["product.pricelist"].create(
            {
                "name": "Public Pricelist",
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "test@test.com",
            }
        )
        cls.product_6 = cls.env["product.product"].create(
            {
                "name": "Test Product 6",
                "type": "consu",
                "list_price": 100.0,
                "standard_price": 70.0,
            }
        )
        cls.product_7 = cls.env["product.product"].create(
            {
                "name": "Test Product 7",
                "type": "consu",
                "list_price": 200.0,
                "standard_price": 150.0,
            }
        )
        cls.excep_no_zip = cls.env["exception.rule"].create(
            {
                "name": "No ZIP code on destination",
                "description": "No ZIP code on destination",
                "sequence": 50,
                "model": "sale.order",
                "code": "failed=not self.partner_shipping_id.zip",
                "active": False,
            }
        )
        cls.excep_no_free = cls.env["exception.rule"].create(
            {
                "name": "No free order",
                "description": "The total can't be 0",
                "sequence": 50,
                "model": "sale.order",
                "exception_type": "by_domain",
                "domain": "[('amount_total', '=', 0)]",
                "active": False,
            }
        )
        cls.exception_partner_sale_warning = cls.env["exception.rule"].create(
            {
                "name": "Customer sale warning",
                "description": "The customer has a sale warning in his form",
                "sequence": 40,
                "model": "sale.order",
                "code": "failed=bool(self.partner_id.sale_warn_msg)",
                "active": False,
            }
        )
        cls.exception_product_sale_warning = cls.env["exception.rule"].create(
            {
                "name": "Product warning",
                "description": "The product has a warning in his form",
                "sequence": 40,
                "model": "sale.order.line",
                "code": "failed=bool(self.product_id.sale_line_warn_msg)",
                "active": False,
            }
        )

    def test_sale_order_exception(self):
        self.sale_exception_confirm = self.env["sale.exception.confirm"]

        self.excep_no_zip.sudo().active = True

        self.partner.zip = False
        p = self.product_6
        so1 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": p.name,
                            "product_id": p.id,
                            "product_uom_qty": 2,
                            "product_uom_id": p.uom_id.id,
                            "price_unit": p.list_price,
                        },
                    )
                ],
                "pricelist_id": self.default_pl.id,
            }
        )

        # confirm quotation
        self.excep_no_zip.active = True
        so1.action_confirm()
        self.assertTrue(so1.state == "draft")
        so1.detect_exceptions()
        self.assertTrue(so1.exception_ids.filtered(lambda x: x == self.excep_no_zip))
        # test all draft so
        so2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": p.name,
                            "product_id": p.id,
                            "product_uom_qty": 3,
                            "product_uom_id": p.uom_id.id,
                            "price_unit": p.list_price,
                        },
                    )
                ],
                "pricelist_id": self.default_pl.id,
            }
        )
        self.env["sale.order"].test_all_draft_orders()
        self.assertTrue(so2.state == "draft")
        # Set ignore_exception flag  (Done after ignore is selected at wizard)
        so1.ignore_exception = True
        so1.action_confirm()
        self.assertTrue(so1.state == "sale")

        # Add a order line to test after SO is confirmed
        p = self.product_7

        # set ignore_exception = False  (Done by onchange of order_line)
        self.assertRaises(
            ValidationError,
            so1.write,
            {
                "ignore_exception": False,
                "order_line": [
                    Command.create(
                        {
                            "name": p.name,
                            "product_id": p.id,
                            "product_uom_qty": 2,
                            "product_uom_id": p.uom_id.id,
                            "price_unit": p.list_price,
                        },
                    )
                ],
            },
        )

        p = self.product_7

        # Set ignore exception True  (Done manually by user)
        so1.write(
            {
                "ignore_exception": True,
                "order_line": [
                    Command.create(
                        {
                            "name": p.name,
                            "product_id": p.id,
                            "product_uom_qty": 2,
                            "product_uom_id": p.uom_id.id,
                            "price_unit": p.list_price,
                        },
                    )
                ],
            }
        )
        self.excep_no_zip.active = False
        so1.with_context(disable_cancel_warning=True).action_cancel()
        so1.action_draft()
        self.assertTrue(not so1.ignore_exception)

        # Simulation the opening of the wizard sale_exception_confirm and
        # set ignore_exception to True
        so_except_confirm = self.sale_exception_confirm.with_context(
            active_id=so1.id, active_ids=so1.ids, active_model=so1._name
        ).create({"ignore": True})
        so_except_confirm.action_confirm()
        self.assertTrue(so1.ignore_exception)
        self.assertEqual(so1.state, "sale")

    def _create_sale_order(self, partner, product):
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = product
        return order_form.save()

    def test_exception_partner_sale_warning(self):
        self.exception_partner_sale_warning.active = True
        sale_order = self._create_sale_order(
            partner=self.partner, product=self.product_6
        )
        sale_order.action_confirm()
        self.partner.sale_warn_msg = "warning"
        sale_order2 = sale_order.copy()
        self.env.company.sale_exception_show_popup = True
        result = sale_order2.action_confirm()
        self.assertEqual(
            result.get("xml_id"), "sale_exception.action_sale_exception_confirm"
        )
        self.assertEqual(sale_order2.state, "draft")
        self.assertTrue(
            sale_order2.exception_ids.filtered(
                lambda x: x == self.exception_partner_sale_warning
            )
        )

    def test_exception_partner_sale_warning_no_popup(self):
        self.exception_partner_sale_warning.active = True
        sale_order = self._create_sale_order(
            partner=self.partner, product=self.product_6
        )
        sale_order.action_confirm()
        self.partner.sale_warn_msg = "warning"
        sale_order2 = sale_order.copy()
        self.env.company.sale_exception_show_popup = False
        result = sale_order2.action_confirm()
        self.assertIsNone(result)
        self.assertEqual(sale_order2.state, "draft")
        self.assertTrue(
            sale_order2.exception_ids.filtered(
                lambda x: x == self.exception_partner_sale_warning
            )
        )

    def test_exception_product_sale_warning(self):
        self.exception_product_sale_warning.active = True
        sale_order = self._create_sale_order(
            partner=self.partner, product=self.product_6
        )
        sale_order.action_confirm()
        self.product_6.sale_line_warn_msg = "warning"
        sale_order2 = sale_order.copy()
        sale_order2.detect_exceptions()
        self.assertTrue(
            sale_order2.exception_ids.filtered(
                lambda x: x == self.exception_product_sale_warning
            )
        )

    def test_exception_no_free(self):
        # No allow ignoring exceptions if the "is_blocking" field is checked
        self.sale_exception_confirm = self.env["sale.exception.confirm"]
        self.excep_no_free.active = True
        self.excep_no_free.is_blocking = True
        p = self.product_6
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": p.name,
                            "product_id": p.id,
                            "product_uom_qty": 2,
                            "product_uom_id": p.uom_id.id,
                            "price_unit": 0,
                        },
                    )
                ],
            }
        )
        sale_order.action_confirm()
        so_except_confirm = self.sale_exception_confirm.with_context(
            **{
                "active_id": sale_order.id,
                "active_ids": [sale_order.id],
                "exception_ids": [self.excep_no_free.id],
                "active_model": sale_order._name,
            }
        ).create({"ignore": True})
        with self.assertRaisesRegex(
            UserError,
            "The exceptions can not be ignored, because some of them are blocking.",
        ):
            so_except_confirm.action_confirm()
        self.assertFalse(sale_order.ignore_exception)
        self.assertTrue(sale_order.state == "draft")
