# -*- coding: utf-8 -*-
# Copyright 2016 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestMrpLink(TransactionCase):

    def setUp(self):
        super(TestMrpLink, self).setUp()
        sale_obj = self.env['sale.order']
        partner_values = {'name': 'Test Partner'}
        partner = self.env['res.partner'].create(partner_values)
        mrp_route_id = self.env.ref('mrp.route_warehouse0_manufacture').id
        mto_route_id = self.env.ref('stock.route_warehouse0_mto').id
        product_values = {'name': 'Product Test',
                          'list_price': 50,
                          'type': 'product',
                          'route_ids': [(6, 0, [mrp_route_id, mto_route_id])]}
        product = self.env['product.product'].create(product_values)
        self.product_uom_unit = self.env.ref('product.product_uom_unit')
        bom_vals = {
            'product_tmpl_id': product.product_tmpl_id.id,
            'product_id': product.id,
            'type': 'normal',
        }
        self.env['mrp.bom'].create(bom_vals)
        values = {
            'partner_id': partner.id,
            'order_line': [(0, 0, {
                'name': product.name,
                'product_id': product.id,
                'product_uom': self.product_uom_unit.id,
                'price_unit': product.list_price,
                'product_uom_qty': 1})],
        }
        self.sale_order = sale_obj.create(values)

    def test_01_mrp_link(self):
        """Check manufactured order is linked to sale order."""
        self.sale_order.action_confirm()
        mo = self.env['mrp.production'].search(
            [('sale_order_id', '=', self.sale_order.id)])
        self.assertEqual(len(mo), 1)
        action = self.sale_order.action_view_manufacturing_order()
        mo_ids = action.get('domain')[0][2]
        self.assertEqual(mo_ids, [mo.id])
