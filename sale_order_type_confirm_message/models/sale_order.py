# Copyright 2021 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        if (
            not self.env.context.get("bypass_double_confirmation")
            and self.type_id.has_confirmation_message
        ):
            return {
                "type": "ir.actions.act_window",
                "name": _("Confirm Order"),
                "res_model": "sale.order.type.confirm.wizard",
                "view_type": "form",
                "view_mode": "form",
                "target": "new",
            }
        return super().action_confirm()
