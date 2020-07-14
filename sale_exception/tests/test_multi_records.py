# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.addons.sale.tests.test_sale_order import TestSaleOrder


class TestSaleExceptionMultiRecord(TestSaleOrder):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

    def test_sale_order_exception(self):
        exception_no_sol = self.env.ref("sale_exception.excep_no_sol")
        exception_no_free = self.env.ref("sale_exception.excep_no_free")
        exception_no_dumping = self.env.ref("sale_exception.excep_no_dumping")
        exceptions = exception_no_sol + exception_no_free + exception_no_dumping
        exceptions.write({"active": True})

        partner = self.env.ref("base.res_partner_1")
        p = self.env.ref("product.product_product_7")
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

        so2 = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "partner_invoice_id": partner.id,
                "partner_shipping_id": partner.id,
                "pricelist_id": self.env.ref("product.list0").id,
            }
        )

        so3 = self.env["sale.order"].create(
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
                            "price_unit": p.list_price / 2,
                        },
                    )
                ],
                "pricelist_id": self.env.ref("product.list0").id,
            }
        )

        orders = so1 + so2 + so3
        for order in orders:
            # ensure init state
            self.assertTrue(order.state == "draft")
            self.assertTrue(len(order.exception_ids) == 0)

        self.env["sale.order"].test_all_draft_orders()

        # basic tests

        self.assertTrue(so1.state == "draft")
        self.assertTrue(len(so1.exception_ids) == 0)

        self.assertTrue(so2.state == "draft")
        self.assertTrue(exception_no_sol in so2.exception_ids)
        self.assertTrue(exception_no_free in so2.exception_ids)

        self.assertTrue(so3.state == "draft")
        self.assertTrue(exception_no_dumping in so3.exception_ids)
        self.assertEqual(
            so3.order_line[0].exceptions_summary,
            (
                "<ul>"
                "<li>No dumping: <i>A product is sold cheaper than his cost.</i></li>"
                "</ul>"
            ),
        )

        # test return value of detect_exception()

        all_detected = orders.detect_exceptions()
        self.assertTrue(exception_no_sol.id in all_detected)
        self.assertTrue(exception_no_dumping.id in all_detected)
        self.assertTrue(exception_no_free.id in all_detected)

        one_two_detected = (so1 + so2).detect_exceptions()
        self.assertTrue(exception_no_sol.id in one_two_detected)
        self.assertFalse(exception_no_dumping.id in one_two_detected)
        self.assertTrue(exception_no_free.id in one_two_detected)

        # test subset of rules
        def new_rule_domain(self=False):
            return [("model", "=", "sale.order"), ("id", "!=", exception_no_sol.id)]

        orders._rule_domain = new_rule_domain
        # even if the rule is excluded from the search
        # it should still be present on the sale order
        orders.detect_exceptions()
        all_detected = orders.mapped("exception_ids").ids
        self.assertTrue(exception_no_sol.id in all_detected)
        self.assertTrue(exception_no_dumping.id in all_detected)
        self.assertTrue(exception_no_free.id in all_detected)
