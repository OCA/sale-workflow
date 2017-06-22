# -*- coding: utf-8 -*-
# Copyright 2013-2014 Camptocamp SA - Guewen Baconnier
# © 2016 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleProcurementGroupByLine(TransactionCase):

    def setUp(self):
        super(TestSaleProcurementGroupByLine, self).setUp()
        # Required Models
        self.product_model = self.env['product.product']
        self.product_ctg_model = self.env['product.category']
        self.sale_model = self.env['sale.order']
        self.order_line_model = self.env['sale.order.line']
        # Customer
        self.customer = self.env.ref('base.res_partner_2')
        # Warehouse
        self.warehouse_id = self.env.ref('stock.warehouse0')
        # Create product category
        self.product_ctg = self._create_product_category()
        # Create Products
        self.new_product1 = self._create_product('test_product1')
        self.new_product2 = self._create_product('test_product2')
        self._create_sale_order()

    def _create_product_category(self):
        product_ctg = self.product_ctg_model.create({
            'name': 'test_product_ctg',
        })
        return product_ctg

    def _create_product(self, name):
        product = self.product_model.create({
            'name': name,
            'categ_id': self.product_ctg.id,
            'type': 'product',
        })
        return product

    def _create_sale_order(self):
        """Create a Sale Order."""
        self.sale = self.sale_model.create({
            'partner_id': self.customer.id,
            'warehouse_id': self.warehouse_id.id,
            'picking_policy': 'direct',
        })
        self.line1 = self.order_line_model.create({
            'order_id': self.sale.id,
            'product_id': self.new_product1.id,
            'product_uom_qty': 10.0,
            'name': 'Sale Order Line Demo',
        })
        self.line2 = self.order_line_model.create({
            'order_id': self.sale.id,
            'product_id': self.new_product2.id,
            'product_uom_qty': 5.0,
            'name': 'Sale Order Line Demo',
        })
        return self.sale

    def test_procurement_group_by_line(self):
        self.sale.action_confirm()
        self.assertEqual(self.line2.procurement_group_id,
                         self.line1.procurement_group_id,
                         """Both Sale Order line should belong
                         to Procurement Group""")
        self.assertEqual(self.line1.procurement_ids.product_qty,
                         self.line1.product_uom_qty,
                         """The Procurement quantity should
                         match to the quantity ordered""")
        self.sale._compute_get_picking_ids()
        self.picking_ids = self.env['stock.picking'].\
            search([('group_id', 'in', self.line2.procurement_group_id.ids)])
        self.assertTrue(self.picking_ids,
                        'Procurement Group should have picking')
