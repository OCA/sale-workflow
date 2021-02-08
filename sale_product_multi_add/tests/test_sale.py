# © 2016  Cédric Pigeon, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import odoo.tests.common as common


class TestSale(common.TransactionCase):
    def setUp(self):
        super(TestSale, self).setUp()

        self.product_9 = self.env.ref("product.product_product_9")
        self.product_11 = self.env.ref("product.product_product_11")

    def test_import_product(self):
        """ Create SO
            Import products
            Check products are presents
        """

        so = self.env["sale.order"].create(
            {"partner_id": self.env.ref("base.res_partner_2").id}
        )

        wiz_obj = self.env["sale.import.products"]
        wizard = wiz_obj.with_context(active_id=so.id, active_model="sale.order")

        products = [(6, 0, [self.product_9.id, self.product_11.id])]

        wizard_id = wizard.create({"products": products})
        wizard_id.create_items()
        wizard_id.items[0].quantity = 4
        wizard_id.items[1].quantity = 6
        wizard_id.select_products()

        self.assertEqual(len(so.order_line), 2)

        for line in so.order_line:
            if line.product_id.id == self.product_9.id:
                self.assertEqual(line.product_uom_qty, 4)
            else:
                self.assertEqual(line.product_uom_qty, 6)

    def test_import_product_discount(self):
        pricelist1 = self.env['product.pricelist'].create(
            {
                "name": "Pricelist 1",
                'discount_policy': 'without_discount',
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "compute_price": "percentage",
                            "base": "list_price",
                            "percent_price": 10,
                            "applied_on": "3_global",
                            "name": "Discount 1",
                        },
                    )
                ],
            }
        )
        group_discount_id = self.ref("product.group_discount_per_so_line")
        self.env.user.write({"groups_id": [(4, group_discount_id.id, 0)]})
        so = self.env["sale.order"].create(
            {"partner_id": self.env.ref("base.res_partner_2").id,
             "pricelist_id": pricelist1.id}
        )

        wiz_obj = self.env["sale.import.products"]
        wizard = wiz_obj.with_context(active_id=so.id,
                                      active_model="sale.order")

        products = [(6, 0, [self.product_9.id])]

        wizard_id = wizard.create({"products": products})
        wizard_id.create_items()
        wizard_id.items[0].quantity = 4
        wizard_id.select_products()

        self.assertEqual(len(so.order_line), 1)
        line = so.order_line[0]
        self.assertEqual(line.discount, 10)
