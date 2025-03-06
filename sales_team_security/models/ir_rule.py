# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, tools
from odoo.osv import expression
from odoo.tools import config


class IrRule(models.Model):
    _inherit = "ir.rule"

    @api.model
    @tools.conditional(
        "xml" not in config["dev_mode"],
        tools.ormcache(
            "self.env.uid",
            "self.env.su",
            "model_name",
            "mode",
            "tuple(self._compute_domain_context_values())",
        ),
    )
    def _compute_domain(self, model_name, mode="read"):
        """Inject extra domain for restricting partners when the user
        has the group 'Sales / User: Own Documents Only'.
        """
        res = super()._compute_domain(model_name, mode=mode)
        user = self.env.user
        group_my_records = "sales_team.group_sale_salesman"
        group_all_records = "sales_team.group_sale_salesman_all_leads"
        if model_name == "res.partner" and not self.env.su:
            if user.has_group(group_my_records) and not user.has_group(
                group_all_records
            ):
                domain_followers = [
                    "|",
                    ("message_partner_ids", "in", user.partner_id.ids),
                    ("id", "=", user.partner_id.id),
                ]
                domain_user = [("user_id", "in", [user.id, False])]
                extra_domain = expression.OR([domain_followers, domain_user])
                extra_domain = expression.normalize_domain(extra_domain)
                res = expression.AND([extra_domain] + [res])
        return res
