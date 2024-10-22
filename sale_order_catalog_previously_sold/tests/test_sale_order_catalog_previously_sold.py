# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.exceptions import UserError
from odoo.tests import Form, TransactionCase


class TestSaleOrderCatalogPreviouslySold(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env.ref("base.res_partner_2")
        cls.product = cls.env.ref("product.product_product_9")
        sale_order_form = Form(cls.env["sale.order"])
        sale_order_form.partner_id = cls.partner
        cls.sale_order = sale_order_form.save()

    def test_sale_order_carrier_auto_assign(self):
        previously_sold = (
            self.env["product.product"]
            .with_context(order_id=self.sale_order.id)
            .search([("product_catalog_product_previously_sold", "=", True)])
        )
        self.assertNotIn(self.product, previously_sold)

        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as line_form:
            line_form.product_id = self.product
        sale_order_form.save()

        previously_sold = (
            self.env["product.product"]
            .with_context(order_id=self.sale_order.id)
            .search([("product_catalog_product_previously_sold", "=", True)])
        )
        self.assertIn(self.product, previously_sold)

        self.assertTrue(
            self.product.with_context(
                order_id=self.sale_order.id
            ).product_catalog_product_previously_sold
        )
        self.assertFalse(self.product.product_catalog_product_previously_sold)

        self.assertRaises(
            UserError,
            self.env["product.product"]
            .with_context(order_id=self.sale_order.id)
            .search,
            [("product_catalog_product_previously_sold", "in", [True])],
        )
