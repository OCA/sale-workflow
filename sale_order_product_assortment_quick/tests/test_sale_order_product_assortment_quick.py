from odoo.tests import SavepointCase


class TestSaleOrderProductAssortmentQuick(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.filter_obj = cls.env["ir.filters"]
        cls.product_obj = cls.env["product.product"]
        cls.sale_order_obj = cls.env["sale.order"]
        cls.partner_1 = cls.env["res.partner"].create({"name": "Test partner 1"})
        cls.partner_2 = cls.env["res.partner"].create({"name": "Test partner 2"})

    def test_sale_order_get_domain_add_products(self):
        product_1 = self.product_obj.create({"name": "Test product 1"})
        assortment_with_whitelist = self.filter_obj.create(
            {
                "name": "Test Assortment 1",
                "model_id": "product.product",
                "domain": [],
                "is_assortment": True,
                "partner_ids": [(4, self.partner_1.id)],
                "whitelist_product_ids": [(4, product_1.id)],
            }
        )
        sale_order_1 = self.sale_order_obj.create({"partner_id": self.partner_1.id})
        self.assertEquals(
            sale_order_1.allowed_product_ids,
            assortment_with_whitelist.whitelist_product_ids,
        )
        self.assertTrue(sale_order_1.has_allowed_products)

        domain_tuple = ("id", "in", product_1.ids)
        self.assertIn(domain_tuple, sale_order_1._get_domain_add_products())
        sale_order_1.write({"partner_id": self.partner_2.id})
        self.assertNotIn(domain_tuple, sale_order_1._get_domain_add_products())
