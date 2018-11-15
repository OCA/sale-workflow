# -*- coding: utf-8 -*-
# Copyright 2013-2014 Camptocamp SA - Guewen Baconnier
# © 2016 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from openerp import models, api, fields
from openerp.tools import float_compare


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _prepare_procurement_group_by_line(self, line):
        """ Hook to be able to use line data on procurement group """
        return self._prepare_procurement_group()

    ###
    # OVERRIDE to find sale.order.line's picking
    ###

    @api.multi
    @api.depends('order_line')
    def _compute_get_picking_ids(self):
        for sale in self:
            group_ids = set([line.procurement_group_id.id
                             for line in sale.order_line
                             if line.procurement_group_id])
            if not any(group_ids):
                self.picking_ids = []
                continue
            self.picking_ids = self.env['stock.picking'].search(
                [('group_id', 'in', list(group_ids))])

    picking_ids = fields.One2many('stock.picking',
                                  compute='_compute_get_picking_ids',
                                  method=True,
                                  string='Picking associated to this sale')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _get_procurement_group_key(self):
        """ Return a key with priority to be used to regroup lines in multiple
        procurement groups

        """
        return 8, self.order_id.id

    @api.multi
    def _action_procurement_create(self):
        """
        Create procurements based on quantity ordered.
        If the quantity is increased, new procurements are created.
        If the quantity is decreased, no automated action is taken.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit'
                                                                'of Measure')
        new_procs = self.env['procurement.order']  # Empty recordset
        groups = {}
        for line in self:
            if line.state != 'sale' or not line.product_id._need_procurement():
                continue
            qty = 0.0
            for proc in line.procurement_ids:
                qty += proc.product_qty
            if float_compare(qty, line.product_uom_qty,
                             precision_digits=precision) >= 0:
                continue

            # Group the sales order lines with same procurement group
            # according to the group key
            group_id = groups.get(line._get_procurement_group_key())
            if not group_id:
                vals = line.order_id._prepare_procurement_group_by_line(line)
                group_id = self.env["procurement.group"].create(vals)
                groups[line._get_procurement_group_key()] = group_id
            line.procurement_group_id = group_id

            vals = line._prepare_order_line_procurement(
                group_id=line.procurement_group_id.id)
            vals['product_qty'] = line.product_uom_qty - qty
            new_proc = self.env["procurement.order"].create(vals)
            new_procs += new_proc
        new_procs.run()
        return new_procs

    procurement_group_id = fields.Many2one('procurement.group',
                                           'Procurement group', copy=False)
