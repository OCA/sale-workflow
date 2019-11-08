# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    existing_qty = fields.Float(
        "Existing quantity",
        compute="_compute_get_existing_qty",
        help="Quantity already planned or shipped (stock movements \
            already created)",
        readonly=True,
    )

    pending_qty_to_deliver = fields.Boolean(
        compute='_compute_get_existing_qty',
        store=True,
        readonly=True,
        string='There is Pending qty to add to a delivery')

    @api.multi
    def _action_launch_stock_rule(self):
        for line in self:
            if line.order_id.manual_delivery \
                    and line.product_id.type != "service":
                return False
            else:
                return super()._action_launch_stock_rule()

    @api.depends('move_ids', 'move_ids.state', 'move_ids.location_id',
                 'move_ids.location_dest_id')
    @api.multi
    def _compute_get_existing_qty(self):
        """Computes the remaining quantity on sale order lines, based on related
        done stock moves.
        """
        for line in self:
            rounding = line.company_id.currency_id.rounding
            qty = 0.0
            for move in line.move_ids.filtered(
                lambda r: r.state not in ("draft", "cancel") and not r.scrapped
            ):
                if move.location_dest_id.usage == "customer":
                    qty += move.product_uom._compute_quantity(
                        move.product_uom_qty, line.product_uom
                    )
                elif move.location_dest_id.usage == "internal" \
                        and move.to_refund:
                    qty -= move.product_uom._compute_quantity(
                        move.product_uom_qty, line.product_uom
                    )
            line.existing_qty = qty
            if float_compare(
                    line.product_uom_qty,
                    line.existing_qty, precision_rounding=rounding):
                line.pending_qty_to_deliver = True
            else:
                line.pending_qty_to_deliver = False
