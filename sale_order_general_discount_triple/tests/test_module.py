from odoo.addons.base.tests.common import BaseCommon


class TestModule(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id |= cls.env.ref("sale.group_discount_per_so_line")
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test Partner", "sale_discount": 10}
        )
        cls.product = cls.env.ref("product.product_product_4")
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test multi-currency",
                "currency_id": cls.env.ref("base.USD").id,
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "1_product",
                            "compute_price": "percentage",
                            "product_tmpl_id": cls.product.product_tmpl_id.id,
                            "percent_price": 20,
                        },
                    ),
                ],
            }
        )
        cls.env["ir.config_parameter"].create(
            {
                "key": "sale_order_general_discount_triple.general_discount",
                "value": "discount2",
            }
        )
        cls.env["ir.config_parameter"].create(
            {
                "key": "sale_order_general_discount_triple.pricelist_discount",
                "value": "discount1",
            }
        )

    def test_action_result(self):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id}),
                ],
            }
        )
        sale_order.order_line.product_uom_qty = 2
        for line in sale_order.order_line:
            self.assertEqual(line.discount2, 10)
            self.assertEqual(line.discount1, 20)
