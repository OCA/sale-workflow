# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.tests import Form, common


class TestSaleStockPrebookCase(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner_form = Form(cls.env["res.partner"])
        partner_form.name = "Test partner"
        cls.partner = partner_form.save()

        no_prebook_stock_route_id = (
            cls.env["stock.location.route"]
            .sudo()
            .create(
                {
                    "name": "Test Route Without Prebook Stock",
                    "no_sale_stock_prebook": True,
                }
            )
        )
        # prebook product
        product_form = Form(cls.env["product.product"])
        product_form.name = "Test Product 1"
        product_form.type = "product"
        cls.product_1 = product_form.save()
        # non-prebook product
        product_form = Form(cls.env["product.product"])
        product_form.name = "Test Product 22"
        product_form.type = "product"
        product_form.route_ids.add(no_prebook_stock_route_id)
        cls.product_2 = product_form.save()

        cls.sale = cls.create_sale_order([(cls.product_1, 3), (cls.product_2, 3)])
        cls.sale2 = cls.create_sale_order([(cls.product_2, 3)])

    @classmethod
    def create_sale_order(cls, products):
        sale_order_form = Form(cls.env["sale.order"])
        sale_order_form.partner_id = cls.partner
        for product, qty in products:
            with sale_order_form.order_line.new() as order_line_form:
                order_line_form.product_id = product
                order_line_form.product_uom_qty = qty
        return sale_order_form.save()
