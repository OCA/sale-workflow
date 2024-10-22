from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    lot_id_readonly = fields.Boolean(compute="_compute_lot_id_readonly")
    lot_id = fields.Many2one(
        "stock.lot",
        "Lot",
        copy=False,
        compute="_compute_lot_id",
        store=True,
        readonly=False,
    )

    def _prepare_procurement_values(self, group_id=False):
        vals = super()._prepare_procurement_values(group_id=group_id)
        if self.lot_id:
            vals["restrict_lot_id"] = self.lot_id.id
        return vals

    @api.depends("product_id")
    def _compute_lot_id(self):
        for sol in self:
            if sol.product_id != sol.lot_id.product_id:
                sol.lot_id = False

    @api.depends("state", "company_id.allow_to_change_lot_on_confirmed_so")
    def _compute_lot_id_readonly(self):
        for line in self:
            company = line.company_id or self.env.company
            # line.ids checks whether it's a new record not yet saved
            line.lot_id_readonly = (
                line.ids
                and line.state in ["sale", "done", "cancel"]
                and not company.allow_to_change_lot_on_confirmed_so
            )

    def write(self, vals):
        res = super().write(vals)
        allow_to_change_lot = self.env.company.allow_to_change_lot_on_confirmed_so
        if "lot_id" in vals and (
            allow_to_change_lot or self.order_id.state not in ["sale", "done"]
        ):
            self.move_ids.write({"restrict_lot_id": vals.get("lot_id")})
        elif "lot_id" in vals and not allow_to_change_lot:
            raise UserError(_("You can't change the lot on confirmed sale order."))
        return res
