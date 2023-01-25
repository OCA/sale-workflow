# Copyright 2011 Akretion, Sodexis
# Copyright 2018 Akretion
# Copyright 2019 Camptocamp SA
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import Form, TransactionCase


class TestSaleException(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

    def test_sale_order_exception(self):
        self.sale_exception_confirm = self.env["sale.exception.confirm"]

        exception = self.env.ref("sale_exception.excep_no_zip").sudo()
        exception.active = True

        partner = self.env.ref("base.res_partner_1")
        partner.zip = False
        p = self.env.ref("product.product_product_6")
        so1 = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "partner_invoice_id": partner.id,
                "partner_shipping_id": partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": p.name,
                            "product_id": p.id,
                            "product_uom_qty": 2,
                            "product_uom": p.uom_id.id,
                            "price_unit": p.list_price,
                        },
                    )
                ],
                "pricelist_id": self.env.ref("product.list0").id,
            }
        )

        # confirm quotation
        exception = self.env.ref("sale_exception.excep_no_zip")
        exception.active = True
        so1.action_confirm()
        self.assertTrue(so1.state == "draft")
        so1.detect_exceptions()
        self.assertTrue(so1.exception_ids.filtered(lambda x: x == exception))
        # test all draft so
        so2 = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "partner_invoice_id": partner.id,
                "partner_shipping_id": partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": p.name,
                            "product_id": p.id,
                            "product_uom_qty": 3,
                            "product_uom": p.uom_id.id,
                            "price_unit": p.list_price,
                        },
                    )
                ],
                "pricelist_id": self.env.ref("product.list0").id,
            }
        )
        self.env["sale.order"].test_all_draft_orders()
        self.assertTrue(so2.state == "draft")
        # Set ignore_exception flag  (Done after ignore is selected at wizard)
        so1.ignore_exception = True
        so1.action_confirm()
        self.assertTrue(so1.state == "sale")

        # Add a order line to test after SO is confirmed
        p = self.env.ref("product.product_product_7")

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
                            "product_uom": p.uom_id.id,
                            "price_unit": p.list_price,
                        },
                    )
                ],
            },
        )

        p = self.env.ref("product.product_product_7")

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
                            "product_uom": p.uom_id.id,
                            "price_unit": p.list_price,
                        },
                    )
                ],
            }
        )
        exception.active = False
        so1.action_cancel()
        so1.action_draft()
        self.assertTrue(not so1.ignore_exception)

        # Simulation the opening of the wizard sale_exception_confirm and
        # set ignore_exception to True
        so_except_confirm = self.sale_exception_confirm.with_context(
            **{"active_id": so1.id, "active_ids": [so1.id], "active_model": so1._name}
        ).create({"ignore": True})
        so_except_confirm.action_confirm()
        self.assertTrue(so1.ignore_exception)

    def _create_sale_order(self, partner, product):
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = product
        return order_form.save()

    def test_exception_partner_sale_warning(self):
        exception = self.env.ref("sale_exception.exception_partner_sale_warning")
        exception.active = True
        partner = self.env.ref("base.res_partner_1")
        sale_order = self._create_sale_order(
            partner=partner, product=self.env.ref("product.product_product_6")
        )
        sale_order.action_confirm()
        partner.sale_warn = "warning"
        sale_order2 = sale_order.copy()
        sale_order2.detect_exceptions()
        self.assertTrue(sale_order2.exception_ids.filtered(lambda x: x == exception))

    def test_exception_product_sale_warning(self):
        exception = self.env.ref("sale_exception.exception_product_sale_warning")
        exception.active = True
        product = self.env.ref("product.product_product_6")
        sale_order = self._create_sale_order(
            partner=self.env.ref("base.res_partner_1"), product=product
        )
        sale_order.action_confirm()
        product.sale_line_warn = "warning"
        sale_order2 = sale_order.copy()
        sale_order2.detect_exceptions()
        self.assertTrue(sale_order2.exception_ids.filtered(lambda x: x == exception))
