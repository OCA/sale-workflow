# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. <contact@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestPartnerDefaultSaleWarehouse(TransactionCase):

    def setUp(self):
        super(TestPartnerDefaultSaleWarehouse, self).setUp()
        self.sale_order_model = self.env['sale.order']
        self.partner_model = self.env['res.partner']
        self.warehouse_model = self.env['stock.warehouse']
        self.company_partner = self.env.ref('base.main_partner')

        self.wh1 = self.warehouse_model.create(
            {'partner_id': self.company_partner.id,
             'name': 'WH1',
             'code': 'WH1'})

        self.customer = self.partner_model.create(
            {'name': 'Partner1'})
        self.ship_to = self.partner_model.create(
            {'name': 'Ship-to for Partner 1',
             'parent_id': self.customer.id,
             'sale_warehouse_id': self.wh1.id}
        )
        self.product = self.env.ref('product.product_product_4')
        self.sale_order1 = self.sale_order_model.create({
            'partner_id': self.customer.id,
            'order_policy': 'manual',
            'order_line': [(0, 0, {
                'name': self.product.name,
                'product_uom_qty': 1,
                'price_unit': self.product.list_price,
                'product_id': self.product.id,
                'product_uom': self.product.uom_id.id})],
        })
        self.sale_order1.partner_shipping_id = self.ship_to.id

    def test_sale_default_warehouse(self):
        """Test that the sales order has the new warehouse"""
        # Checks that OU in sale order and stock picking matches or not.
        self.assertEqual(self.sale_order1.warehouse_id.id,
                         self.wh1.id,
                         'The sales order does not contain the default '
                         'warehouse indicated in the delivery address '
                         'partner.')
