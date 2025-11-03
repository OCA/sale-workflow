from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _selection_product_tracking(self):
        return self.env["product.product"].fields_get(
            allfields=["tracking"],
        )["tracking"]["selection"]

    product_tracking = fields.Selection(
        selection=_selection_product_tracking,
        compute="_compute_product_tracking",
    )
    lot_id = fields.Many2one(
        "stock.lot",
        "Lot",
        copy=False,
        compute="_compute_lot_id",
        inverse="_inverse_lot_id",
        store=True,
        readonly=False,
        precompute=True,
    )

    def _prepare_procurement_values(self):
        vals = super()._prepare_procurement_values()
        if self.lot_id:
            vals["restrict_lot_id"] = self.lot_id.id
        return vals

    @api.depends("product_id")
    def _compute_product_tracking(self):
        for sol in self:
            sol.product_tracking = sol.product_id.tracking or sol.product_tracking

    @api.depends("product_id")
    def _compute_lot_id(self):
        for sol in self:
            if sol.product_id != sol.lot_id.product_id:
                sol.lot_id = False

    def _inverse_lot_id(self):
        for item in self.filtered(
            lambda x: x.product_id and x.product_tracking != "none" and x.move_ids
        ):
            moves = item.move_ids.filtered(lambda x: x.restrict_lot_id)
            if any(move.state == "done" for move in moves):
                raise ValidationError(
                    self.env._(
                        "You can't modify the Lot/Serial number "
                        "because some stock move has already been done."
                    )
                )
            pending_moves = moves.filtered(lambda x: x.state != "cancel")
            if pending_moves:
                pending_moves._set_restrict_lot_id_from_sol(item.lot_id)
