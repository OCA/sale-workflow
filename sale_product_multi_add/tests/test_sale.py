# © 2016  Cédric Pigeon, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import odoo.tests.common as common


class TestSale(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env.user.groups_id |= cls.env.ref("sale.group_discount_per_so_line")

        cls.product_9 = cls.env.ref("product.product_product_9")
        cls.product_11 = cls.env.ref("product.product_product_11")

        cls.pricelist = cls.env["product.pricelist"].create({"name": "My Pricelist"})
        cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.pricelist.id,
                "applied_on": "3_global",
                "base": "list_price",
                "compute_price": "formula",
                "price_discount": 10,
            }
        )
        cls.product_9.list_price = 20

        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.ref("base.res_partner_2").id,
                "pricelist_id": cls.pricelist.id,
            }
        )

        wiz_obj = cls.env["sale.import.products"].with_context(
            active_id=cls.order.id, active_model="sale.order"
        )
        cls.wizard = wiz_obj.create({})

    def test_import_product(self):
        self.wizard.products = self.product_9 | self.product_11
        self.wizard.create_items()
        self.wizard.items[0].quantity = 4
        self.wizard.items[1].quantity = 6
        self.wizard.select_products()

        self.assertEqual(len(self.order.order_line), 2)

        for line in self.order.order_line:
            if line.product_id.id == self.product_9.id:
                self.assertEqual(line.product_uom_qty, 4)
            else:
                self.assertEqual(line.product_uom_qty, 6)

    def test_pricelist_discount_included(self):
        self.pricelist.discount_policy = "with_discount"
        self.wizard.products = self.product_9
        self.wizard.create_items()
        self.wizard.items.quantity = 1
        self.wizard.select_products()
        assert self.order.order_line.price_unit == 18  # 20 * (1 - 10%)
        assert self.order.order_line.discount == 0

    def test_pricelist_discount_excluded(self):
        self.pricelist.discount_policy = "without_discount"
        self.wizard.products = self.product_9
        self.wizard.create_items()
        self.wizard.items.quantity = 1
        self.wizard.select_products()
        assert self.order.order_line.price_unit == 20
        assert self.order.order_line.discount == 10
