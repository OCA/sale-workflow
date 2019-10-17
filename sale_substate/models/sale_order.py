# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ExceptionRule(models.Model):
    _inherit = "base.substate.type"

    model = fields.Selection(selection_add=[("sale.order", "Sale order")])


class SaleOrder(models.Model):
    _inherit = ["sale.order", "base.substate.mixin"]
    _name = "sale.order"

    @api.constrains("substate_id", "state")
    def check_substate_id_value(self):
        sale_states = dict(self._fields["state"].selection)
        for order in self:
            target_state = (
                order.substate_id.target_state_value_id.target_state_value
            )
            if order.state != target_state:
                raise ValidationError(
                    _(
                        'The substate "%s" is not define for the state "%s" but for "%s" '
                    )
                    % (
                        order.substate_id.name,
                        _(sale_states[order.state]),
                        _(sale_states[target_state]),
                    )
                )
