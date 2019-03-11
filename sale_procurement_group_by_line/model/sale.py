# -*- coding: utf-8 -*-
# Copyright 2013-2014 Camptocamp SA - Guewen Baconnier
# © 2016 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _prepare_procurement_group_by_line(self, line):
        """ Hook to be able to use line data on procurement group """
        return self._prepare_procurement_group()

    ##
    # OVERRIDE to find sale.order.line's picking
    ##

    @api.multi
    @api.depends('order_line')
    def _compute_picking_ids(self):
        super(SaleOrder, self)._compute_picking_ids()
        for sale in self:
            group_ids = set([line.procurement_group_id.id
                             for line in sale.order_line
                             if line.procurement_group_id])
            if not group_ids:
                sale.picking_ids = []
                continue
            sale.picking_ids = self.env['stock.picking'].search(
                [('group_id', 'in', list(group_ids))])
            sale.delivery_count = len(sale.picking_ids)


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
            for proc in line.procurement_ids.filtered(
                    lambda r: r.state != 'cancel'):
                qty += proc.product_qty
            if float_compare(qty, line.product_uom_qty,
                             precision_digits=precision) >= 0:
                continue

            # Group the sales order lines with same procurement group
            # according to the group key
            group_id = line.procurement_group_id or False
            for l in line.order_id.order_line:
                g_id = l.procurement_group_id or False
                if g_id:
                    groups[l._get_procurement_group_key()] = g_id
            if not group_id:
                group_id = groups.get(line._get_procurement_group_key())
            if not group_id:
                vals = line.order_id._prepare_procurement_group_by_line(line)
                group_id = self.env["procurement.group"].create(vals)
            line.procurement_group_id = group_id

            vals = line._prepare_order_line_procurement(
                group_id=line.procurement_group_id.id)
            vals['product_qty'] = line.product_uom_qty - qty
            new_proc = self.env["procurement.order"].with_context(
                procurement_autorun_defer=True).create(vals)
            new_proc.message_post_with_view(
                'mail.message_origin_link',
                values={'self': new_proc, 'origin': line.order_id},
                subtype_id=self.env.ref('mail.mt_note').id)
            new_procs += new_proc
        new_procs.run()
        super(SaleOrderLine, self)._action_procurement_create()
        return new_procs

    procurement_group_id = fields.Many2one('procurement.group',
                                           'Procurement group', copy=False)
