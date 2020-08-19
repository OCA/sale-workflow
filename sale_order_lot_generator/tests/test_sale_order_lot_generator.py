# © 2017 Akretion, Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as test_common


class TestSaleOrderLotGenerator(test_common.SingleTransactionCase):
    def setUp(self):
        super().setUp()
        self.prd_flipover = self.env.ref("product.product_product_20")
        self.prd_acoustic = self.env.ref("product.product_product_25")
        self.prd_flipover.write(
            {"tracking": "lot", "type": "product", "auto_generate_prodlot": True}
        )
        self.prd_acoustic.write(
            {"tracking": "lot", "type": "product", "auto_generate_prodlot": True}
        )

    def test_sale_order_lot_generator(self):
        # create order
        self.order1 = self.env["sale.order"].create(
            # Lumber partner
            {"partner_id": self.env.ref("base.res_partner_18").id}
        )
        self.sol1 = self.env["sale.order.line"].create(
            {
                "name": "sol1",
                "order_id": self.order1.id,
                "product_id": self.prd_flipover.id,
                "product_uom_qty": 1,
            }
        )
        # confirm orders
        self.order1.action_confirm()
        lot_number = "%s-%03d" % (self.order1.name, 1)
        self.assertEqual(self.sol1.lot_id.name, lot_number)
        # add second line after order confirm
        self.sol2 = self.env["sale.order.line"].create(
            {
                "name": "sol1",
                "order_id": self.order1.id,
                "product_id": self.prd_acoustic.id,
                "product_uom_qty": 1,
            }
        )
        lot_number = "%s-%03d" % (self.order1.name, 2)
        self.assertEqual(self.sol2.lot_id.name, lot_number)
        for line in self.order1.picking_ids.move_line_ids:
            if line.product_id.id == self.prd_flipover.id:
                self.assertEqual(line.lot_id, self.sol1.lot_id)
            if line.product_id.id == self.prd_acoustic.id:
                self.assertEqual(line.restrict_lot_id, self.sol2.lot_id)
