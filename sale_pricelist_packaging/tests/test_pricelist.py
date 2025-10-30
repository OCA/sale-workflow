# Copyright 2023 Sergio Corato
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import Form, SavepointCase


class TestPricelist(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        config = Form(cls.env["res.config.settings"])
        config.group_product_pricelist = True
        config.product_pricelist_setting = "basic"
        config.group_stock_packaging = True
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.product = cls.env.ref("product.product_product_5")
        cls.pricelist = cls.env.ref("product.list0")

        cls.packaging1 = cls.env["product.packaging"].create(
            {
                "name": "Test1",
                "product_id": cls.product.id,
                "qty": 10,
            }
        )
        cls.packaging2 = cls.env["product.packaging"].create(
            {
                "name": "Test2",
                "product_id": cls.product.id,
                "qty": 20,
            }
        )
        cls.env["product.pricelist.item"].create(
            [
                {
                    "applied_on": "0_product_variant",
                    "pricelist_id": cls.pricelist.id,
                    "product_id": cls.product.id,
                    "fixed_price": 100,
                    "packaging_id": cls.packaging1.id,
                },
                {
                    "applied_on": "0_product_variant",
                    "pricelist_id": cls.pricelist.id,
                    "product_id": cls.product.id,
                    "fixed_price": 200,
                    "packaging_id": cls.packaging2.id,
                },
                {
                    "applied_on": "0_product_variant",
                    "pricelist_id": cls.pricelist.id,
                    "product_id": cls.product.id,
                    "fixed_price": 10,
                },
            ]
        )

    def test_packaging_1(self):
        sale_form = Form(self.env["sale.order"])
        sale_form.partner_id = self.partner
        sale_form.pricelist_id = self.pricelist
        with sale_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.product_uom_qty = 20
            line_form.product_packaging = self.packaging1
        sale = sale_form.save()

        self.assertEqual(sale.order_line.price_unit, 100)

    def test_packaging_2(self):
        sale_form = Form(self.env["sale.order"])
        sale_form.partner_id = self.partner
        sale_form.pricelist_id = self.pricelist
        with sale_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.product_uom_qty = 20
            line_form.product_packaging = self.packaging2
        sale = sale_form.save()

        self.assertEqual(sale.order_line.price_unit, 200)

    def test_without_packaging(self):
        sale_form = Form(self.env["sale.order"])
        sale_form.partner_id = self.partner
        sale_form.pricelist_id = self.pricelist
        with sale_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.product_uom_qty = 20

        sale = sale_form.save()
        self.assertEqual(sale.order_line.price_unit, 10)
