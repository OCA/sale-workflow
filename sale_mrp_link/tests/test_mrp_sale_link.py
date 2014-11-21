# -*- coding: utf-8 -*-
# Copyright 2018 Alex Comba - Agile Business Group
# Copyright 2016-2018 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSaleMrpLink(TransactionCase):

    def setUp(self):
        super(TestSaleMrpLink, self).setUp()
        self.partner = self.env.ref('base.res_partner_2')
        self.warehouse = self.env.ref('stock.warehouse0')
        route_manufacture = self.warehouse.manufacture_pull_id.route_id.id
        route_mto = self.warehouse.mto_pull_id.route_id.id
        self.product_a = self._create_product(
            'Product A', route_ids=[(6, 0, [route_manufacture, route_mto])])
        self.product_b = self._create_product(
            'Product B', route_ids=[(6, 0, [route_manufacture, route_mto])])
        self.product_c = self._create_product('Product C', route_ids=[])
        self.product_d = self._create_product('Product D', route_ids=[])

    def _create_bom(self, template):
        return self.env['mrp.bom'].create({
            'product_tmpl_id': template.id,
            'type': 'normal'})

    def _create_bom_line(self, bom, product, qty):
        self.env['mrp.bom.line'].create({
            'bom_id': bom.id,
            'product_id': product.id,
            'product_qty': qty})

    def _create_product(self, name, route_ids):
        return self.env['product.product'].create({
            'name': name,
            'type': 'product',
            'route_ids': route_ids})

    def _create_sale_order(self, partner):
        return self.env['sale.order'].create({'partner_id': partner.id})

    def _create_sale_order_line(self, sale_order, product, qty, price):
        self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': product.id,
            'price_unit': price,
            'product_uom_qty': qty})

    def test_sale_to_only_one_mo(self):
        """Check manufactured order is linked to the sale order."""
        bom = self._create_bom(self.product_a.product_tmpl_id)
        self._create_bom_line(bom, self.product_c, 1)
        so = self._create_sale_order(self.partner)
        self._create_sale_order_line(so, self.product_a, 1, 10.0)
        so.action_confirm()
        mo = self.env['mrp.production'].search(
            [('sale_order_id', '=', so.id)])
        self.assertEqual(len(mo), 1)
        action = so.action_view_production()
        res_id = action['res_id']
        self.assertEqual(res_id, mo.id)

    def test_sale_to_several_mo(self):
        """Check manufactured orders are linked to the sale order."""
        bom_b = self._create_bom(self.product_b.product_tmpl_id)
        self._create_bom_line(bom_b, self.product_d, 1)
        bom_a = self._create_bom(self.product_a.product_tmpl_id)
        self._create_bom_line(bom_a, self.product_c, 1)
        self._create_bom_line(bom_a, self.product_b, 1)
        so = self._create_sale_order(self.partner)
        self._create_sale_order_line(so, self.product_a, 1, 10.0)
        so.action_confirm()
        mo = self.env['mrp.production'].search(
            [('sale_order_id', '=', so.id)])
        self.assertEqual(len(mo), 2)
        action = so.action_view_production()
        mo_ids = action.get('domain')[0][2]
        self.assertEqual(mo.ids, mo_ids)
