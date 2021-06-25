# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def manage_activities(self):
        # manage activities creation
        model_id = self.env["ir.model"]._get(self._name).id
        activity_types = self.env["mail.activity.type"].search(
            [
                ("res_model_id", "=", model_id),
                ("category", "=", "validation"),
                ("previous_type_ids", "=", False),
            ]
        )
        Activity = self.env["mail.activity"]
        for rec in self:
            for activity_type in activity_types:
                Activity.create(rec._prepare_activity_data(activity_type))

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.manage_activities()
        return res

    def _prepare_activity_data(self, activity_type):
        self.ensure_one()
        res = {
            "res_id": self.id,
            "res_model_id": activity_type.res_model_id.id,
            "activity_type_id": activity_type.id,
            "summary": activity_type.summary,
            "automated": True,
        }
        return res

    def action_confirm(self):
        # check if some validation activities remain for each sale order
        # given in self
        # All done activities are unlinked
        # (see action_feedback of mail.activity model)
        if not self.check_validation_activities_todo():
            raise UserError(
                _(
                    "All validation checks must be done before "
                    "confirming the sale order."
                )
            )
        return super().action_confirm()

    def action_draft(self):
        super().action_draft()
        for rec in self:
            # delete old activities
            rec.activity_ids.filtered(
                lambda a: a.activity_type_id.category == "validation"
            ).unlink()
            # generate new ones
            rec.manage_activities()
