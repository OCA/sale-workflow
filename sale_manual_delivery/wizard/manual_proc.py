# -*- coding: utf-8 -*-
# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from odoo.tools import float_compare
from odoo.exceptions import UserError
from odoo.tools.translate import _


class ManualDelivery(models.TransientModel):
    """Creates procurements manually"""
    _name = "manual.delivery"
    _order = 'create_date desc'

    @api.model
    def default_get(self, fields):
        res = super(ManualDelivery, self).default_get(
            fields)
        active_model = self.env.context['active_model']
        if active_model == 'sale.order.line':
            sale_ids = self.env.context['active_ids'] or []
            lines = self.env['sale.order.line'].browse(sale_ids).filtered(
                lambda s: s.pending_qty_to_deliver)
        elif active_model == 'sale.order':
            sale_ids = self.env.context['active_ids'] or []
            lines = self.env['sale.order'].browse(sale_ids).mapped(
                'order_line').filtered(
                lambda s: s.pending_qty_to_deliver)
        res['sale_line_ids'] = [(6, 0, lines.ids)]
        return res

    @api.onchange("partner_id", "date_planned")
    def onchange_partner_id(self):
        return {
            "domain": {
                "partner_id": [
                    "&",
                    "|",
                    ("id", "=", self.mapped(
                        'line_ids.order_line_id.order_id.partner_id.id')),
                    ("parent_id", "=", self.mapped(
                        'line_ids.order_line_id.order_id.partner_id.id')),
                    ("id", "!=", self.partner_id.id),
                ]
            }
        }

    @api.onchange('line_ids')
    def onchange_line_ids(self):
        lines = []
        for line in self.sale_line_ids:
            if (not line.existing_qty == line.product_uom_qty and
                    line.product_id.type != 'service'):
                vals = {
                    'order_line_id': line.id,
                    'ordered_qty': line.product_uom_qty,
                    'existing_qty': line.existing_qty,
                    'to_ship_qty': line.product_uom_qty - line.existing_qty
                }
                lines.append((0, 0, vals))
        self.update({'line_ids': lines})

    date_planned = fields.Date(
        string='Date Planned'
    )

    sale_line_ids = fields.Many2many('sale.order.line')
    line_ids = fields.One2many(
        'manual.delivery.line',
        'manual_delivery_id',
        string='Lines to validate',
    )
    carrier_id = fields.Many2one(
        'delivery.carrier',
        string='Delivery Method'
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Delivery Address'
    )
    route_id = fields.Many2one(
        'stock.location.route', string='Use specific Route',
        domain=[('sale_selectable', '=', True)],
        ondelete='restrict',
        help="Leave it blank to use the same route that is in the sale line")

    @api.multi
    def record_picking(self):
        proc_order_obj = self.env['procurement.order']
        proc_group_obj = self.env['procurement.group']
        proc_group_dict = {}
        for wizard in self:
            date_planned = wizard.date_planned
            for line in wizard.mapped('line_ids.order_line_id'):
                order = line.order_id
                if not order.procurement_group_id:
                    vals = order._prepare_procurement_group()
                    if wizard.date_planned:
                        vals['date_planned'] = date_planned
                    order_proc_group_to_use = \
                        order.procurement_group_id = proc_group_obj.create(
                            vals)
                else:
                    order_proc_group_to_use = self.env[
                        'procurement.group'].search(
                        [
                            ('procurement_ids.sale_line_id.order_id', '=',
                             order.id),
                            ('date_planned', '=', date_planned),
                        ], limit=1
                    )
                    if not order_proc_group_to_use:
                        order_proc_group_to_use = order.procurement_group_id.\
                            copy({
                                'date_planned': date_planned, }
                            )
                proc_group_dict[order.id] = order_proc_group_to_use
            new_procs = proc_order_obj
            for wiz_line in wizard.line_ids:
                rounding = wiz_line.order_line_id.company_id.\
                    currency_id.rounding
                carrier_id = wizard.carrier_id if wizard.carrier_id else \
                    wiz_line.order_line_id.order_id.carrier_id
                if float_compare(wiz_line.to_ship_qty,
                                 wiz_line.ordered_qty - wiz_line.existing_qty,
                                 precision_rounding=rounding) > 0.0:
                    raise UserError(_('You can not deliver more than the '
                                      'remaining quantity. If you need to do '
                                      'so, please edit the sale order first.'))
                if float_compare(wiz_line.to_ship_qty, 0, 2):
                    so_id = wiz_line.order_line_id.order_id
                    proc_group_to_use = proc_group_dict[so_id.id]
                    vals = wiz_line.order_line_id.\
                        _prepare_order_line_procurement(
                            group_id=proc_group_to_use.id)
                    if date_planned:
                        vals['date_planned'] = date_planned
                    if wizard.route_id:
                        vals["route_ids"] = [(6, 0, [wizard.route_id.id])]
                    vals['product_qty'] = wiz_line.to_ship_qty
                    if carrier_id:
                        vals['carrier_id'] = carrier_id.id
                    vals["partner_dest_id"] = wizard.partner_id.id
                    vals['manual_delivery'] = True
                    new_proc = proc_order_obj.create(vals)
                    new_proc.message_post_with_view(
                        'mail.message_origin_link',
                        values={'self': new_proc,
                                'origin': wiz_line.order_line_id.order_id},
                        subtype_id=self.env.ref('mail.mt_note').id)
                    new_procs |= new_proc
            new_procs.run()
