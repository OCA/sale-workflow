# -*- coding: utf-8 -*-
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    returned_qty = fields.Float(
        string='Returned',
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_returned_qty')

    @api.multi
    def _compute_returned_qty(self):
        for rec in self:
            qty = 0.0
            for move in rec.procurement_ids.mapped('move_ids').filtered(
                    lambda r: r.state == 'done' and not r.scrapped):
                if move.location_dest_id.usage == "internal":
                    if move.origin_returned_move_id:
                        qty += move.product_uom._compute_quantity(
                            move.product_uom_qty, rec.product_uom)
                elif (move.location_dest_id.usage != "customer" and
                      move.to_refund_so):
                    qty -= move.product_uom._compute_quantity(
                        move.product_uom_qty, rec.product_uom)
            rec.returned_qty = qty

    def _prepare_order_line_procurement(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_order_line_procurement(
            group_id)
        if self.env.context.get('manual', False):
            res.update(product_qty=self.env.context.get('qty'))
            res.update(product_id=self.env.context.get('product'))
            res.update(product_uom=self.env.context.get('uom'))
        return res

    @api.multi
    def _action_procurement_create(self):
        if self.env.context.get('manual', False):
            new_procs = self.env['procurement.order']
            for line in self:
                vals = line._prepare_order_line_procurement(
                    group_id=line.procurement_group_id.id)
                new_proc = self.env["procurement.order"].with_context(
                    procurement_autorun_defer=True).create(vals)
                new_proc.message_post_with_view('mail.message_origin_link',
                    values={'self': new_proc, 'origin': line.order_id},
                    subtype_id=self.env.ref('mail.mt_note').id)
                new_procs += new_proc
            new_procs.run()
            return new_procs
        else:
            return super(SaleOrderLine, self)._action_procurement_create()
