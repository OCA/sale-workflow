# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def manage_activities(self):
        # manage activities creation
        activity_types = self.env["mail.activity.type"].search(
            [
                ("res_model", "=", self._name),
                ("category", "=", "validation"),
                ("previous_type_ids", "=", False),
            ]
        )
        values = []
        for order in self:
            for activity_type in activity_types:
                values.append(order._prepare_activity_data(activity_type))
        if values:
            self.env["mail.activity"].create(values)

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        orders.manage_activities()
        return orders

    def _prepare_activity_data(self, activity_type):
        self.ensure_one()
        return {
            "res_id": self.id,
            "res_model_id": self.env["ir.model"]._get(activity_type.res_model).id,
            "activity_type_id": activity_type.id,
            "summary": activity_type.summary,
            "automated": True,
        }

    def action_confirm(self):
        # check if some validation activities remain for each sale order
        # given in self
        # All done activities are unlinked
        # (see _action_done of mail.activity model)
        if not self._check_validation_activities_todo():
            raise UserError(
                _(
                    "All validation checks must be done before "
                    "confirming the sale order."
                )
            )
        return super().action_confirm()

    def action_draft(self):
        res = super().action_draft()
        # delete old activities if necessary
        acts = self.activity_ids.filtered(
            lambda a: a.activity_type_id.category == "validation"
        )
        if acts:
            acts.unlink()
        # generate new ones
        self.manage_activities()
        return res
