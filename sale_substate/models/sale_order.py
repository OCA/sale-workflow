# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class BaseSubstateType(models.Model):
    _inherit = "base.substate.type"

    model = fields.Selection(selection_add=[("sale.order", "Sale order")])


class SaleOrder(models.Model):
    _inherit = ["sale.order", "base.substate.mixin"]
    _name = "sale.order"

    @api.constrains("substate_id", "state")
    def check_substate_id_value(self):
        sale_states = dict(self._fields["state"].selection)
        for order in self:
            target_state = order.substate_id.target_state_value_id.target_state_value
            if order.substate_id and order.state != target_state:
                raise ValidationError(
                    _(
                        'The substate "%s" is not defined for the state'
                        ' "%s" but for "%s" '
                    )
                    % (
                        order.substate_id.name,
                        _(sale_states[order.state]),
                        _(sale_states[target_state]),
                    )
                )

    @api.multi
    def _track_template(self, tracking):
        res = super(SaleOrder, self)._track_template(tracking)
        first_sale = self[0]
        changes, tracking_value_ids = tracking[first_sale.id]
        if "substate_id" in changes and first_sale.substate_id.mail_template_id:
            res["substate_id"] = (
                first_sale.substate_id.mail_template_id,
                {
                    "auto_delete_message": True,
                    "subtype_id": self.env["ir.model.data"].xmlid_to_res_id(
                        "mail.mt_note"
                    ),
                    "notif_layout": "mail.mail_notification_light",
                },
            )
        return res
