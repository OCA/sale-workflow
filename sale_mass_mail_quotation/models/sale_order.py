# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_open_mass_mail_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "quotation.mass.mail.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_sale_order_ids": [(6, 0, self.env.context.get("active_ids"))],
            },
        }

    def _find_mail_template(self):
        force_tmpl = self.env.context.get("mass_so_mail_template")
        if force_tmpl:
            return force_tmpl
        return super()._find_mail_template()
