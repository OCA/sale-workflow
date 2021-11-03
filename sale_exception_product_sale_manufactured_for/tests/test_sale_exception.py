# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import SavepointCase


class TestSaleException(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.exception = cls.env.ref(
            "sale_exception_product_sale_manufactured_for.exception_partner_can_order"
        )
        cls.exception.active = True

        partner_order = cls.env.ref("base.res_partner_1")
        cls.partner_manufactured_for = cls.env.ref("base.res_partner_3")
        cls.product = cls.env.ref("product.product_product_6")
        cls.product.product_tmpl_id.manufactured_for_partner_ids |= (
            cls.partner_manufactured_for
        )

        cls.sale = cls.env["sale.order"].create(
            {
                "partner_id": partner_order.id,
                "partner_invoice_id": partner_order.id,
                "partner_shipping_id": partner_order.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 1,
                        },
                    )
                ],
            }
        )

    def test_commercial_partner_not_valid(self):
        self.sale.partner_id.commercial_partner_id = self.env.ref("base.res_partner_2")
        self.sale.action_confirm()
        self.assertEqual(self.sale.state, "draft")
        self.assertEqual(len(self.sale.exception_ids), 1)
        self.assertEqual(self.sale.exception_ids[0], self.exception)

    def test_commercial_partner_is_valid(self):
        self.sale.partner_id.commercial_partner_id = self.sale.order_line[
            0
        ].product_id.product_tmpl_id.manufactured_for_partner_ids[0]
        self.sale.action_confirm()
        self.assertEqual(self.sale.state, "sale")
        self.assertFalse(self.sale.exception_ids)

    def test_commercial_partner_empty(self):
        self.sale.partner_id.commercial_partner_id = False
        self.sale.action_confirm()
        self.assertEqual(self.sale.state, "draft")
        self.assertEqual(len(self.sale.exception_ids), 1)
        self.assertEqual(self.sale.exception_ids[0], self.exception)

    def test_product_without_limits_partner_with_commercial_entity(self):
        self.product.product_tmpl_id.manufactured_for_partner_ids = False
        self.sale.partner_id.commercial_partner_id = self.partner_manufactured_for
        self.sale.action_confirm()
        self.assertEqual(self.sale.state, "sale")
        self.assertFalse(self.sale.exception_ids)

    def test_product_without_limits_partner_without_commercial_entity(self):
        self.product.product_tmpl_id.manufactured_for_partner_ids = False
        self.sale.partner_id.commercial_partner_id = False
        self.sale.action_confirm()
        self.assertEqual(self.sale.state, "sale")
        self.assertFalse(self.sale.exception_ids)
