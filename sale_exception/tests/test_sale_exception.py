# Copyright 2011 Akretion, Sodexis
# Copyright 2018 Akretion
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import ValidationError
from odoo.tests import SavepointCase


class TestSaleException(SavepointCase):
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
                    (
                        0,
                        0,
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
        so1.action_confirm()
        self.assertTrue(so1.state == "draft")
        # test all draft so
        so2 = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "partner_invoice_id": partner.id,
                "partner_shipping_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
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
                    (
                        0,
                        0,
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
                    (
                        0,
                        0,
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
            {"active_id": so1.id, "active_ids": [so1.id], "active_model": so1._name}
        ).create({"ignore": True})
        so_except_confirm.action_confirm()
        self.assertTrue(so1.ignore_exception)
