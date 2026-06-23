from odoo.tests.common import Form, TransactionCase


class TestModule(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test Partner", "sale_discount": 10}
        )
        cls.product = cls.env.ref("product.product_product_4")
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test multi-currency",
                "discount_policy": "without_discount",
                "currency_id": cls.env.ref("base.USD").id,
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "3_global",
                            "compute_price": "percentage",
                            "percent_price": 20,
                        },
                    ),
                ],
            }
        )
        setting_form = Form(cls.env["res.config.settings"])
        setting_form.general_discount = "discount2"
        setting_form.pricelist_discount = "discount1"
        setting_form.group_discount_per_so_line = True
        setting_form.save().set_values()

    def test_action_result(self):
        sale_form = Form(self.env["sale.order"])
        sale_form.partner_id = self.partner
        sale_form.pricelist_id = self.pricelist
        with sale_form.order_line.new() as line:
            line.product_id = self.product
        sale = sale_form.save()
        self.assertEqual(sale.order_line.discount2, 10)
        self.assertEqual(sale.order_line.discount1, 20)
