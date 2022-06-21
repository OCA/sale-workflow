from odoo.tests.common import Form, TransactionCase


class TestSaleOrderLine(TransactionCase):
    def test_sale_order_line(self):
        product_obj = self.env["product.template"]
        sale_order_obj = self.env["sale.order"]
        partner_obj = self.env["res.partner"]
        uom_dozen = self.env.ref("uom.product_uom_dozen")

        product_form = Form(product_obj)
        product_form.name = "Test Product"
        self.assertFalse(product_form.sale_uom_id)
        product_form.sale_uom_id = uom_dozen
        product = product_form.save()
        self.assertEqual(product.sale_uom_id.id, uom_dozen.id)

        product_form = Form(product_obj)
        product_form.name = "Test Product 2"
        product_without_sale_uom = product_form.save()
        self.assertFalse(product_without_sale_uom.sale_uom_id)

        partner_form = Form(partner_obj)
        partner_form.name = "Test Customer"
        partner = partner_form.save()

        with Form(sale_order_obj) as sale_order:
            sale_order.partner_id = partner
            with sale_order.order_line.new() as line:
                line.product_id = product.product_variant_id
                self.assertEqual(line.product_uom.id, uom_dozen.id)

        with Form(sale_order_obj) as sale_order:
            sale_order.partner_id = partner
            with sale_order.order_line.new() as line:
                line.product_id = product_without_sale_uom.product_variant_id
                self.assertNotEqual(line.product_uom.id, uom_dozen.id)
