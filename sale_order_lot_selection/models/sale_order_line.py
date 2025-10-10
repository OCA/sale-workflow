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
        """
        Override of write to manage propagation of lot changes to stock moves.

        Behavior
        - If vals does not include lot_id, this method behaves exactly as the
          standard write and returns.
        - If lot_id is present, we compare the original lot per line with the
          new lot after super().write(vals):
          - If the lot did not actually change, the call is a no-op regarding
            stock moves (nothing is propagated and no error is raised).
          - If the order is in draft/quotation (not in sale/done), we propagate
            the change to related stock moves by writing move.restrict_lot_id
            to the new value (which can be a lot id or False).
          - If the order is in sale/done:
            - When the company setting allow_to_change_lot_on_confirmed_so is
              True, we propagate the change to the related stock moves.
            - When the company setting is False, we prevent changing the lot
              and raise a UserError.
        """
        # Capture original lot ids to detect actual changes per record
        original_lots = {rec.id: rec.lot_id.id for rec in self}
        res = super().write(vals)
        if "lot_id" not in vals:
            return res
        allow_to_change_lot = self.env.company.allow_to_change_lot_on_confirmed_so
        for line in self:
            old_lot = original_lots.get(line.id)
            new_lot = line.lot_id.id
            # Only act if there is an actual change
            if new_lot == old_lot:
                continue
            if allow_to_change_lot or line.order_id.state not in ["sale", "done"]:
                # Propagate the new lot restriction to related stock moves
                line.move_ids.write({"restrict_lot_id": new_lot})
            else:
                # Disallow changing the lot on confirmed SO if company setting forbids it
                raise UserError(_("You can't change the lot on confirmed sale order."))
        return res
