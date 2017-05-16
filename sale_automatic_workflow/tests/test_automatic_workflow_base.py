# -*- coding: utf-8 -*-
# Copyright 2014 Camptocamp SA (author: Guewen Baconnier)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestAutomaticWorkflowBase(common.TransactionCase):

    def create_sale_order(self, workflow, override=None):
        sale_obj = self.env['sale.order']
        partner_values = {'name': 'Imperator Caius Julius Caesar Divus'}
        partner = self.env['res.partner'].create(partner_values)
        product_values = {'name': 'Bread',
                          'list_price': 5,
                          'type': 'product'}
        product = self.env['product.product'].create(product_values)
        self.product_uom_unit = self.env.ref('product.product_uom_unit')
        values = {
            'partner_id': partner.id,
            'order_line': [(0, 0, {
                'name': product.name,
                'product_id': product.id,
                'product_uom': self.product_uom_unit.id,
                'price_unit': product.list_price,
                'product_uom_qty': 1})],
            'workflow_process_id': workflow.id,
        }
        if override:
            values.update(override)
        return sale_obj.create(values)

    def create_full_automatic(self, override=None):
        workflow_obj = self.env['sale.workflow.process']
        values = workflow_obj.create({
            'name': 'Full Automatic',
            'picking_policy': 'one',
            'validate_order': True,
            'validate_picking': True,
            'create_invoice': True,
            'validate_invoice': True,
            'invoice_date_is_order_date': True,
        })
        if override:
            values.update(override)
        return values

    def progress(self):
        self.env['automatic.workflow.job'].run()
