# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from unittest import mock

from odoo import Command
from odoo.tests import TransactionCase


class TestSaleExceptionMultiRecord(TransactionCase):
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
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product 7",
                "type": "consu",
                "list_price": 200.0,
                "standard_price": 150.0,
            }
        )
        cls.excep_no_sol = cls.env["exception.rule"].create(
            {
                "name": "No order lines",
                "description": "At least one order line should be present in the sale",
                "sequence": 50,
                "model": "sale.order",
                "exception_type": "by_domain",
                "domain": "[('order_line', '=', False)]",
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
        cls.excep_no_dumping = cls.env["exception.rule"].create(
            {
                "name": "No dumping",
                "description": "A product is sold cheaper than his cost.",
                "sequence": 50,
                "model": "sale.order.line",
                "code": (
                    "failed = obj.product_id.standard_price != 0 and "
                    "obj.product_id.standard_price > obj.price_unit"
                ),
                "active": False,
            }
        )

    def test_sale_order_exception(self):
        exceptions = self.excep_no_sol + self.excep_no_free + self.excep_no_dumping
        exceptions.write({"active": True})

        p = self.product
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

        so2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "pricelist_id": self.default_pl.id,
            }
        )

        so3 = self.env["sale.order"].create(
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
                            "price_unit": p.list_price / 2,
                        },
                    )
                ],
                "pricelist_id": self.default_pl.id,
            }
        )

        orders = so1 + so2 + so3
        # ensure init state
        for order in orders:
            self.assertTrue(order.state == "draft")
            self.assertTrue(len(order.exception_ids) == 0)
        self.assertFalse(so1.order_line[0].is_exception_danger)
        self.assertFalse(so3.order_line[0].is_exception_danger)

        self.env["sale.order"].test_all_draft_orders()

        # basic tests

        self.assertTrue(so1.state == "draft")
        self.assertTrue(len(so1.exception_ids) == 0)
        self.assertFalse(so1.order_line[0].is_exception_danger)

        self.assertTrue(so2.state == "draft")
        self.assertTrue(self.excep_no_sol in so2.exception_ids)
        self.assertTrue(self.excep_no_free in so2.exception_ids)

        self.assertTrue(so3.state == "draft")
        self.assertTrue(self.excep_no_dumping in so3.exception_ids)
        self.assertEqual(
            so3.order_line[0].exceptions_summary,
            (
                "<ul>"
                "<li>No dumping: <i>A product is sold cheaper than his cost.</i></li>"
                "</ul>"
            ),
        )
        self.assertTrue(so3.order_line[0].is_exception_danger)

        # test return value of detect_exception()

        all_detected = orders.detect_exceptions()
        self.assertTrue(self.excep_no_sol.id in all_detected)
        self.assertTrue(self.excep_no_dumping.id in all_detected)
        self.assertTrue(self.excep_no_free.id in all_detected)

        one_two_detected = (so1 + so2).detect_exceptions()
        self.assertTrue(self.excep_no_sol.id in one_two_detected)
        self.assertFalse(self.excep_no_dumping.id in one_two_detected)
        self.assertTrue(self.excep_no_free.id in one_two_detected)

        # test subset of rules
        domain = [
            ("model", "=", "sale.order"),
            ("id", "!=", self.excep_no_sol.id),
        ]
        with mock.patch.object(type(orders), "_rule_domain", return_value=domain):
            # even if the rule is excluded from the search
            # it should still be present on the sale order
            orders.detect_exceptions()
            all_detected = orders.mapped("exception_ids").ids
            self.assertTrue(self.excep_no_sol.id in all_detected)
            self.assertTrue(self.excep_no_dumping.id in all_detected)
            self.assertTrue(self.excep_no_free.id in all_detected)
