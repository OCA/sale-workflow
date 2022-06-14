# © 2016  Cédric Pigeon, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import odoo.tests.common as common


class TestSale(common.TransactionCase):
    def setUp(self):
        super(TestSale, self).setUp()

        self.product_9 = self.env.ref("product.product_product_9")
        self.product_11 = self.env.ref("product.product_product_11")

    def test_import_product(self):
        """Create SO
        Import products
        Check products are presents
        """

        so = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_2").id,
                "picking_policy": "direct",
            }
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
