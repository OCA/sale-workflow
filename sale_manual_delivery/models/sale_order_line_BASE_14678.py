# -*- coding: utf-8 -*-
# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    existing_qty = fields.Float(
        'Existing quantity',
        compute='_compute_get_existing_qty',
        help="Quantity already planned or shipped (stock movements \
            already created)",
        readonly=True,
    )

    @api.multi
    def _action_procurement_create(self):
        for line in self:
            if (line.order_id.manual_delivery and
                    line.product_id.type != 'service'):
                return self.env['procurement.order'].browse()
            else:
                return super(SaleOrderLine, self)._action_procurement_create()

    @api.multi
    def _action_manual_procurement_create(self, product_qty, date_planned,
                                          carrier):
        new_procs = self.env['procurement.order']  # Empty recordset
        for line in self:
            qty = 0.0
            for proc in line.procurement_ids:
                qty += proc.product_qty

            if not line.order_id.procurement_group_id:
                vals = line.order_id._prepare_procurement_group()
                line.order_id.procurement_group_id = self.env[
                    "procurement.group"].create(vals)

            vals = line._prepare_order_line_procurement(
                group_id=line.order_id.procurement_group_id.id)
            vals['date_planned'] = date_planned  # line added
            vals['product_qty'] = product_qty  # line added
            vals['carrier_id'] = carrier.id  # line added
            new_proc = self.env["procurement.order"].create(vals)
            new_proc.message_post_with_view('mail.message_origin_link',
                                            values={'self': new_proc,
                                                    'origin': line.order_id},
                                            subtype_id=self.env.ref(
                                                'mail.mt_note').id)
            new_procs += new_proc
        new_procs.run()
        return new_procs

    @api.multi
    def _compute_get_existing_qty(self):
        """Computes the remai quantity on sale order lines, based on done
        stock moves related to its procurements
        """
        for line in self:
            qty = 0.0
            for move in line.procurement_ids.mapped('move_ids').filtered(
                    lambda r: r.state not in ('draft', 'cancel') and
                    not r.scrapped):
                if move.location_dest_id.usage == "customer":
                    qty += move.product_uom._compute_quantity(
                        move.product_uom_qty,
                        line.product_uom)
                elif (move.location_dest_id.usage == "internal" and
                        move.to_refund_so):
                    qty -= move.product_uom._compute_quantity(
                        move.product_uom_qty,
                        line.product_uom)
            line.existing_qty = qty
