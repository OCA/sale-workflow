# -*- coding: utf-8 -*-
# Copyright 2013-2014 Camptocamp SA - Guewen Baconnier, Yannick Vaucher
# © 2015 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
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
    # OVERRIDE to use sale.order.line's procurement_group_id from lines
    ###
    @api.depends('order_line.procurement_group_id.procurement_ids.state')
    def _get_shipped(self):
        """ As procurement is per sale line basis, we check each line

            If at least a line has no procurement group defined, it means it
            isn't shipped yet.

            Only when all procurement are done or cancelled, we consider
            the sale order as being shipped.

            And if there is no line, we have nothing to ship, thus it isn't
            shipped.

        """
        if not self.order_line:
            self.shipped = False
            return

        # keep empty groups
        groups = set([line.procurement_group_id
                      for line in self.order_line
                      if line.product_id.type != 'service'])
        is_shipped = True
        for group in groups:
            if not group or not group.procurement_ids:
                is_shipped = False
                break
            is_shipped &= all([proc.state in ['cancel', 'done']
                               for proc in group.procurement_ids])
        self.shipped = is_shipped

    ###
    # OVERRIDE to find sale.order.line's picking
    ###

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

    shipped = fields.Boolean(compute='_get_shipped', string='Delivered',
                             store=True)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

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
        for line in self:
            if line.state != 'sale' or not line.product_id._need_procurement():
                continue
            qty = 0.0
            for proc in line.procurement_ids:
                qty += proc.product_qty
            if float_compare(qty, line.product_uom_qty,
                             precision_digits=precision) >= 0:
                continue

            if not line.order_id.procurement_group_id:
                vals = line.order_id._prepare_procurement_group_by_line(line)
                group_id = self.env["procurement.group"].create(vals)
                line.write({'procurement_group_id': group_id.id})

            vals = line.\
                _prepare_order_line_procurement(group_id=line.order_id.
                                                procurement_group_id.id)
            vals['product_qty'] = line.product_uom_qty - qty
            new_proc = self.env["procurement.order"].create(vals)
            new_procs += new_proc
        new_procs.run()
        return new_procs

    @api.multi
    def _get_procurement_group_key(self):
        """ Return a key with priority to be used to regroup lines in multiple
        procurement groups

        """
        return (8, self.order_id.id)

    procurement_group_id = fields.Many2one('procurement.group',
                                           'Procurement group', copy=False)
