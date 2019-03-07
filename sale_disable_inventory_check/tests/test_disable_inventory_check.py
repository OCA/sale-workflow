# Copyright 2017 Komit <http://komit-consulting.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import odoo.tests.common as common


class TestDisableInventoryCheck(common.TransactionCase):

    def setUp(self):
        super(TestDisableInventoryCheck, self).setUp()

        # Create stockable product
        self.product_1 = self.env['product.product'].create({
            'name': 'Product 1',
            'type': 'product',
            'uom_id': self.env.ref('product.product_uom_unit').id,
        })

    def test_disable_inventory_check(self):
        # Create an empty sale order
        order = self.env['sale.order'].new({
            'partner_id': 1,
            'warehouse_id': 1,
            'state': 'draft',
        })
        # Sale product_1 with quantity is 15
        order_line = self.env['sale.order.line'].new({
            'order_id': order.id,
            'product_id': self.product_1.id,
            'product_uom': self.product_1.uom_id.id,
            'product_uom_qty': 15,
        })
        res = order_line._onchange_product_id_check_availability()
        self.assertEqual(res.get('warning', {}), {},
                         "There should not be a warning!!!")
