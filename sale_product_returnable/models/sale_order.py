# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_return_picking_values(self, picking):
        return_type_id = picking.picking_type_id.return_picking_type_id
        return {
            'move_lines': [],
            'partner_id': picking.partner_id.id,
            'picking_type_id': return_type_id.id,
            'state': 'draft',
            'origin': picking.origin,
            'location_id': picking.location_dest_id.id,
            'location_dest_id':
                return_type_id and
                return_type_id.default_location_dest_id.id,
            'move_ids_without_package': [],
            'group_id': self.procurement_group_id.id,
        }

    def _prepare_return_move_values(self, sale_order_line):
        return {
            'product_id': sale_order_line.product_id.return_product_id.id,
            'name': sale_order_line.product_id.return_product_id.name,
            'product_uom_qty': sale_order_line.product_uom_qty,
            'product_uom': sale_order_line.product_id.uom_id.id,
            'origin': self.name,
            'group_id': self.procurement_group_id.id,
        }

    @api.multi
    def action_confirm(self):
        """Action Confirm.
        Create return pickings when confirming sale orders.
        """
        for order in self:
            res = super(SaleOrder, order).action_confirm()
            pickings = order.picking_ids.filtered(
                lambda picking: picking.location_dest_id ==
                order.partner_id.property_stock_customer)
            if pickings and pickings[0]:
                picking = pickings[0]
                new_picking_vals = \
                    order._prepare_return_picking_values(picking)
                has_return = False
                for line in order.order_line:
                    if line.product_id and line.product_id.returnable:
                        new_move_vals = self._prepare_return_move_values(line)
                        new_picking_vals.update({
                            'move_ids_without_package':
                                [(0, 0, new_move_vals)]
                        })
                        has_return = True
                # if we have at least one returnable item, create the return
                if has_return:
                    new_picking = \
                        self.env['stock.picking'].create(new_picking_vals)
                    new_picking.message_post_with_view(
                        'mail.message_origin_link',
                        values={
                            'self': new_picking, 'origin': self},
                        subtype_id=self.env.ref('mail.mt_note').id)
                    new_picking.action_confirm()
                    new_picking.action_assign()
            return res
