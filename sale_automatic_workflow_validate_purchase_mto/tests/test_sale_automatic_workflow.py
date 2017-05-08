# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestAutomaticWorkflow(common.TransactionCase):

    def setUp(self):
        super(TestAutomaticWorkflow, self).setUp()
        workflow_obj = self.env['sale.workflow.process']

        self.workflow = workflow_obj.create({
            'name': 'Full Automatic MTO',
            'picking_policy': 'one',
            'validate_purchase_mto': True,
            'purchase_order_mto_filter_id':
                self.ref('sale_automatic_workflow_validate_purchase_mto.'
                         'automatic_workflow_po_mto_filter'),
            'purchase_order_mto_purchase_filter_id':
                self.ref('sale_automatic_workflow_validate_purchase_mto.'
                         'automatic_workflow_po_mto_purchase_filter'),
            'validate_order': True,
            'validate_picking': True,
            'create_invoice': True,
            'validate_invoice': True,
            'invoice_date_is_order_date': True,
        })

        partner_values = {'name': 'Imperator Caius Julius Caesar Divus'}
        partner = self.env['res.partner'].create(partner_values)
        product_values = {'name': 'Bread',
                          'list_price': 5,
                          'type': 'product'}
        product = self.env['product.product'].create(product_values)
        self.product_uom_unit = self.env.ref('product.product_uom_unit')

        vals = {'name': self.ref('base.res_partner_1'),
                'delay': 3,
                'min_qty': 1,
                'price': 750,
                'product_tmpl_id': product.product_tmpl_id.id
                }
        self.env['product.supplierinfo'].create(vals)

        vals = {'name': 'ROUTE MTO',
                'sequence': 1,
                'product_selectable': True,
                }
        self.route = self.env['stock.location.route'].create(vals)

        vals = {'name': 'OUT => Customer',
                'action': 'move',
                'location_id': self.ref('stock.stock_location_customers'),
                'location_src_id': self.ref('stock.stock_location_output'),
                'procure_method': 'make_to_order',
                'route_id': self.route.id,
                'picking_type_id': self.ref('stock.picking_type_out'),
                }

        self.rule = self.env['procurement.rule'].create(vals)

        vals = {'name': 'Supplier => OUT',
                'action': 'buy',
                'location_id': self.ref('stock.stock_location_output'),
                'location_src_id': self.ref('stock.stock_location_suppliers'),
                'route_id': self.route.id,
                'picking_type_id': self.ref('stock.picking_type_in')}

        self.rule_pick = self.env['procurement.rule'].create(vals)

        values = {
            'partner_id': partner.id,
            'order_line': [(0, 0, {
                'name': product.name,
                'route_id': self.route.id,
                'product_id': product.id,
                'product_uom': self.product_uom_unit.id,
                'price_unit': product.list_price,
                'product_uom_qty': 1})],
            'workflow_process_id': self.workflow.id,
        }

        self.sale_order = self.env['sale.order'].create(values)

    def progress(self):
        self.env['automatic.workflow.job'].run()

    def test_mto(self):
        self.sale_order._onchange_workflow_process_id()
        self.assertEqual(self.sale_order.state, 'draft')
        self.assertEqual(self.sale_order.workflow_process_id, self.workflow)
        self.progress()
        self.assertEqual(self.sale_order.state, 'sale')
        self.assertTrue(self.sale_order.picking_ids)
        self.assertTrue(self.sale_order.invoice_ids)
        invoice = self.sale_order.invoice_ids
        self.assertEqual(invoice.state, 'open')
        self.progress()
        # We check that purchase order is well created
        purchases = self.env['purchase.order'].search([
            ('group_id', '=', self.sale_order.procurement_group_id.id)])
        self.assertEqual(
            1,
            len(purchases),
            'The expected amount of purchase orders is not 1')
        # We check that the purchase order is in the good state
        self.assertEqual(
            'purchase',
            purchases.state,
            'The purchase order is not in the state expected')
