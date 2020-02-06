# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from odoo.tools import float_compare
from odoo.exceptions import UserError
from odoo.tools.translate import _


PARTNER_DOMAIN = """[
    "|", ("id", "=", commercial_partner_id),
    ("parent_id", "=", commercial_partner_id),
]"""


class ManualDelivery(models.TransientModel):
    """Creates procurements manually"""

    _name = "manual.delivery"
    _description = "Manual Delivery"
    _order = "create_date desc"

    @api.model
    def default_get(self, fields):
        if 'line_ids' not in fields:
            return {}
        res = super(ManualDelivery, self).default_get(fields)
        active_model = self.env.context['active_model']
        if active_model == 'sale.order.line':
            sale_ids = self.env.context['active_ids'] or []
            sale_lines = self.env['sale.order.line'].browse(sale_ids).filtered(
                lambda s: s.pending_qty_to_deliver)
        elif active_model == 'sale.order':
            sale_ids = self.env.context['active_ids'] or []
            sale_lines = self.env['sale.order'].browse(sale_ids).mapped(
                'order_line').filtered(lambda s: s.pending_qty_to_deliver)
        if len(sale_lines.mapped('order_id.partner_id')) > 1:
            raise UserError(_('Please select one partner at a time'))
        res['line_ids'] = self.fill_lines(sale_lines)
        partner = sale_lines.mapped('order_id.partner_id')
        res['partner_id'] = partner.id
        res['commercial_partner_id'] = partner.commercial_partner_id.id
        return res

    @api.multi
    def fill_lines(self, sale_lines):
        lines = []

        for line in sale_lines:
            if (not line.existing_qty == line.product_uom_qty and
                    line.product_id.type != 'service'):
                vals = {
                    'product_id': line.product_id.id,
                    'line_description': line.product_id.name,
                    'order_line_id': line.id,
                    'ordered_qty': line.product_uom_qty,
                    'existing_qty': line.existing_qty,
                    'to_ship_qty': line.product_uom_qty - line.existing_qty
                }
                lines.append((0, 0, vals))
        return lines

    date_planned = fields.Datetime(string="Date Planned")
    line_ids = fields.One2many(
        'manual.delivery.line',
        'manual_delivery_id',
        string='Lines to validate',
    )
    carrier_id = fields.Many2one("delivery.carrier", string="Delivery Method")
    route_id = fields.Many2one(
        'stock.location.route', string='Use specific Route',
        domain=[('sale_selectable', '=', True)],
        ondelete='restrict',
        help="Leave it blank to use the same route that is in the sale line")

    partner_id = fields.Many2one(
        "res.partner", domain=PARTNER_DOMAIN, string="Delivery Address")
    commercial_partner_id = fields.Many2one("res.partner")

    @api.multi
    def record_picking(self):
        proc_group_obj = self.env['procurement.group']
        proc_group_dict = {}
        for wizard in self:
            date_planned = wizard.date_planned
            for line in wizard.mapped('line_ids.order_line_id'):
                order = line.order_id

                if not order.procurement_group_id:
                    vals = line._prepare_procurement_values()
                    if wizard.date_planned:
                        vals['date_planned'] = date_planned
                        vals['sale_id'] = order.id
                    order_proc_group_to_use = \
                        order.procurement_group_id = proc_group_obj.create(
                            vals)
                else:
                    order_proc_group_to_use = self.env[
                        'procurement.group'].search(
                        [
                            ('sale_id', '=', order.id),
                            ('date_planned', '=', date_planned),
                        ], limit=1
                    )
                    if not order_proc_group_to_use:
                        order_proc_group_to_use = order.procurement_group_id.\
                            copy({
                                'date_planned': date_planned,
                            })
                proc_group_dict[order.id] = order_proc_group_to_use

            for wiz_line in wizard.line_ids:
                rounding = wiz_line.order_line_id.company_id.\
                    currency_id.rounding
                carrier_id = wizard.carrier_id if wizard.carrier_id else \
                    wiz_line.order_line_id.order_id.carrier_id
                if float_compare(wiz_line.to_ship_qty,
                                 wiz_line.ordered_qty -
                                 wiz_line.existing_qty,
                                 precision_rounding=rounding) > 0.0:
                    raise UserError(_('You can not deliver more than the '
                                      'remaining quantity. If you need to do '
                                      'so, please edit the sale order first.'))
                if float_compare(wiz_line.to_ship_qty, 0, 2):
                    so_id = wiz_line.order_line_id.order_id
                    proc_group_to_use = proc_group_dict[so_id.id]
                    vals = wiz_line.order_line_id.\
                        _prepare_procurement_values(
                            group_id=proc_group_to_use)
                    vals["date_planned"] = date_planned
                    vals["carrier_id"] = carrier_id.id
                    vals["partner_dest_id"] = wizard.partner_id.id
                    if wizard.route_id:
                        vals["route_ids"] = wizard.route_id
                    proc_group_obj.with_context(vals=vals).run(
                        wiz_line.order_line_id.product_id,
                        wiz_line.to_ship_qty,
                        wiz_line.order_line_id.product_uom,
                        so_id.partner_shipping_id.property_stock_customer,
                        wiz_line.order_line_id.name,
                        so_id.name,
                        vals,
                    )
