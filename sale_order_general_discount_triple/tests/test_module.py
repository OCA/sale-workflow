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
        setting_form.pricelist_discount = "discount"
        setting_form.group_discount_per_so_line = True
        setting_form.save().set_values()

    def test_action_result(self):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
            }
        )
        sale_form = Form(sale_order)
        with sale_form.order_line.new() as line:
            line.product_id = self.product
        sale = sale_form.save()
        for line in sale.order_line:
            self.assertEqual(line.discount2, 10)
            self.assertEqual(line.discount, 20)
