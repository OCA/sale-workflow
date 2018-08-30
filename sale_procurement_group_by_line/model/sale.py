# Copyright 2013-2014 Camptocamp SA - Guewen Baconnier
# © 2016-18 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    picking_ids = fields.One2many('stock.picking', 'sale_id',
                                  string='Pickings')

    @api.model
    def _prepare_procurement_group(self):
        vals = {
            'name': self.name,
            'move_type': self.picking_policy,
            'sale_id': self.id,
            'partner_id': self.partner_shipping_id.id,
        }
        return vals

    @api.model
    def _prepare_procurement_group_by_line(self, line):
        """ Hook to be able to use line data on procurement group """
        vals = self._prepare_procurement_group()
        vals.update({'sale_line_id': line.id})
        return vals


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    procurement_group_id = fields.Many2one('procurement.group',
                                           'Procurement group', copy=False)

    @api.multi
    def _get_procurement_group_key(self):
        """ Return a key with priority to be used to regroup lines in multiple
        procurement groups

        """
        return 8, self.order_id.id

    @api.multi
    def _action_launch_procurement_rule(self):
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        errors = []
        groups = {}
        for line in self:
            if line.state != 'sale' or line.product_id.type not in (
                    'consu', 'product'):
                continue
            qty = 0.0
            for move in line.move_ids.filtered(lambda r: r.state != 'cancel'):
                qty += move.product_uom._compute_quantity(
                    move.product_uom_qty, line.product_uom,
                    rounding_method='HALF-UP')
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

            values = line._prepare_procurement_values(group_id=group_id)
            product_qty = line.product_uom_qty - qty

            procurement_uom = line.product_uom
            quant_uom = line.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().get_param
            if procurement_uom.id != quant_uom.id and get_param(
                    'stock.propagate_uom') != '1':
                product_qty = line.product_uom._compute_quantity(
                    product_qty, quant_uom, rounding_method='HALF-UP')
                procurement_uom = quant_uom

            try:
                self.env['procurement.group'].run(
                    line.product_id, product_qty, procurement_uom,
                    line.order_id.partner_shipping_id.property_stock_customer,
                    line.name, line.order_id.name, values)
            except UserError as error:
                errors.append(error.name)

        if errors:
            raise UserError('\n'.join(errors))
        return super(SaleOrderLine, self)._action_launch_procurement_rule()
