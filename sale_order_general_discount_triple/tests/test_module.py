from odoo.tests.common import Form, TransactionCase


class TestModule(TransactionCase):
    def test_action_result(self):
        setting_obj = self.env["res.config.settings"]
        sale_order_obj = self.env["sale.order"]
        partner_obj = self.env["res.partner"]
        product_obj = self.env["product.product"]

        product_form = Form(product_obj)
        product_form.name = "Test Product"
        product = product_form.save()

        partner_form = Form(partner_obj)
        partner_form.name = "Test Partner"
        partner = partner_form.save()
        setting_form = Form(setting_obj)
        setting_form.general_discount = "discount2"
        setting_form.save().set_values()

        with Form(sale_order_obj) as sale_order:
            sale_order.partner_id = partner
            sale_order.general_discount = 5
            with sale_order.order_line.new() as line:
                line.product_id = product
                self.assertEqual(sale_order.general_discount, 5)
