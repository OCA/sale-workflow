# Copyright 2024 Roger Sans <roger.sans@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        if res.invoice_user_id and res.move_type == "out_invoice":
            res.message_unsubscribe([res.invoice_user_id.partner_id.id])
        return res

    def write(self, vals):
        res = super().write(vals)
        if self.invoice_user_id and self.move_type == "out_invoice":
            self.message_unsubscribe([self.invoice_user_id.partner_id.id])
        return res
