# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.tests import common
from odoo.exceptions import ValidationError


class TestSaleDeliveryBlock(common.TransactionCase):

    def setUp(self):
        super(TestSaleDeliveryBlock, self).setUp()
        self.so_model = self.env['sale.order']
        self.sol_model = self.env['sale.order.line']
        self.usr_model = self.env['res.users']
        self.block_model = self.env['sale.delivery.block.reason']
        group_ids = [
            self.env.ref(
                'sale_stock_picking_blocking.group_sale_delivery_block').id,
            self.env.ref('sales_team.group_sale_manager').id,
        ]
        user_dict = {
            'name': 'User test',
            'login': 'tua@example.com',
            'password': 'base-test-passwd',
            'email': 'armande.hruser@example.com',
            'groups_id': [(6, 0, group_ids)],
        }
        self.user_test = self.usr_model.create(user_dict)
        # Create product:
        prod_dict = {
            'name': 'test product',
            'type': 'product',
        }
        product = self.env['product.product'].sudo(self.user_test).create(
            prod_dict)
        # Create Sales order and lines:
        so_dict = {
            'partner_id': self.env.ref('base.res_partner_1').id,
        }
        self.sale_order = self.so_model.sudo(self.user_test).create(so_dict)
        sol_dict = {
            'order_id': self.sale_order.id,
            'product_id': product.id,
            'product_uom_qty': 1.0,
        }
        self.sale_order_line = self.sol_model.create(sol_dict)

    def test_check_auto_done(self):
        # Set active auto done configuration
        self.env['ir.values'].set_default('sale.config.settings',
                                          'auto_done_setting', 1)
        block_reason = self.block_model.sudo(self.user_test).create({
            'name': 'Test Block.'})
        so = self.sale_order
        # Check settings constraints
        with self.assertRaises(ValidationError):
            so.write({
                'delivery_block_id': block_reason.id,
            })

    def procurement_comp(self, so):
        """count created procurements"""
        count = 0
        for line in so.order_line:
            count += len(line.procurement_ids)
        return count

    def test_no_block(self):
        """Tests if normal behaviour without block."""
        so = self.sale_order
        so.action_confirm()
        proc = self.procurement_comp(so)
        self.assertNotEqual(proc, 0, 'A procurement order should have been '
                                     'made')

    def test_sale_stock_picking_blocking(self):
        # Create Sales order block reason:
        block_reason = self.block_model.sudo(self.user_test).create({
            'name': 'Test Block.'})
        so = self.sale_order
        so.write({
            'delivery_block_id': block_reason.id,
        })
        so.action_confirm()
        self.procurement_comp(so)
        proc = self.procurement_comp(so)
        self.assertEqual(proc, 0, 'The procurement should have been blocked')
        # Remove block
        so.action_remove_delivery_block()
        proc = self.procurement_comp(so)
        self.assertNotEqual(proc, 0, 'A procurement order should have been '
                                     'made')
