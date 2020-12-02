from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    lot_id = fields.Many2one("stock.production.lot", "Lot", copy=False)

    def _prepare_procurement_values(self, group_id=False):
        vals = super()._prepare_procurement_values(group_id=group_id)
        if self.lot_id:
            vals['restrict_lot_id'] = self.lot_id.id
        return vals

    @api.onchange("product_id")
    def product_id_change(self):
        super().product_id_change()
        self.lot_id = False

    @api.onchange("product_id")
    def _onchange_product_id_set_lot_domain(self):
        available_lot_ids = []
        if self.order_id.warehouse_id and self.product_id:
            location = self.order_id.warehouse_id.lot_stock_id
            quants = self.env["stock.quant"].read_group(
                [
                    ("product_id", "=", self.product_id.id),
                    ("location_id", "child_of", location.id),
                    ("quantity", ">", 0),
                    ("lot_id", "!=", False),
                ],
                ["lot_id"],
                "lot_id",
            )
            available_lot_ids = [quant["lot_id"][0] for quant in quants]
        self.lot_id = False
        return {"domain": {"lot_id": [("id", "in", available_lot_ids)]}}

    def assign_move_with_lots(self):
        if self.env.context.get("skip_check_lot_selection_move", False):
            return True
        for move in self.move_ids:
            if move.state == "confirmed":
                move._action_assign()
                move.refresh()
            if (
                move.state != "assigned"
            ):
                raise UserError(
                    _("Can't reserve products for lot %s") % self.lot_id.name
                )
