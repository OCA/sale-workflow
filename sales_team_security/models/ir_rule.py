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
        group1 = "sales_team.group_sale_salesman"
        group2 = "sales_team_security.group_sale_team_manager"
        group3 = "sales_team.group_sale_salesman_all_leads"
        if model_name == "res.partner" and not self.env.su:
            # if user.has_group(group_my_records) and not user.has_group(
            #     group_all_records
            # ):
            #     domain_followers = [
            if user.has_group(group1) and not user.has_group(group3):
                extra_domain = [
                    "|",
                    ("message_partner_ids", "in", user.partner_id.ids),
                    "|",
                    ("id", "=", user.partner_id.id),
                ]
                # domain_user = [("user_id", "in", [user.id, False])]
                # extra_domain = expression.OR([domain_followers, domain_user])
                if user.has_group(group2):
                    # Ver todos los contactos de su equipo
                    team_user_ids = user.sale_team_id.member_ids.ids
                    extra_domain += [
                        ("user_id", "in", team_user_ids + [False]),
                    ]
                else:
                    # Ver solo propios y sin asignar
                    extra_domain += [
                        ("user_id", "in", [user.id, False]),
                    ]

                extra_domain = expression.normalize_domain(extra_domain)
                res = expression.AND([extra_domain] + [res])
        return res
