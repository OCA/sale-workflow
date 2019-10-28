# Copyright 2013-2014 Camptocamp SA - Guewen Baconnier
# © 2016 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _prepare_procurement_group_by_line(self, line):
        """ Hook to be able to use line data on procurement group """
        return {'name': line.order_id.name}


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _get_procurement_group_key(self):
        """ Return a key with priority to be used to regroup lines in multiple
        procurement groups

        """
        return 8, self.order_id.id

    @api.multi
    def _action_launch_stock_rule(self):
        """
        Launch procurement group run method.
        """
        precision = self.env['decimal.precision'].\
            precision_get('Product Unit of Measure')
        errors = []
        groups = {}
        for line in self:
            if line.state != 'sale' or line.product_id.type not in (
                    'consu', 'product'):
                continue
            qty = line._get_qty_procurement()
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
                vals.update({
                    'move_type': line.order_id.picking_policy,
                    'sale_id': line.order_id.id,
                    'partner_id': line.order_id.partner_shipping_id.id,
                })
                group_id = self.env['procurement.group'].create(vals)
            else:
                # In case the procurement group is already created and the
                # order was cancelled, we need to update certain values
                # of the group.
                updated_vals = {}
                if group_id.partner_id != line.order_id.partner_shipping_id:
                    updated_vals.update(
                        {'partner_id': line.order_id.partner_shipping_id.id})
                if group_id.move_type != line.order_id.picking_policy:
                    updated_vals.update(
                        {'move_type': line.order_id.picking_policy})
                if updated_vals:
                    group_id.write(updated_vals)
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
        return super(SaleOrderLine, self)._action_launch_stock_rule()

    procurement_group_id = fields.Many2one('procurement.group',
                                           'Procurement group', copy=False)
