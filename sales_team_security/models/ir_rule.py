# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, tools, SUPERUSER_ID
from odoo.osv import expression
from odoo.tools import config


class IrRule(models.Model):
    _inherit = 'ir.rule'

    @api.model
    @tools.conditional(
        'xml' not in config['dev_mode'],
        tools.ormcache(
            'self._uid', 'model_name', 'mode',
            'tuple(self._context.get(k) for k in self._compute_domain_keys())'
        )
    )
    def _compute_domain(self, model_name, mode="read"):
        """Inject extra domain for restricting partners when the user
        has the group 'Sales / User: Own Documents Only'.
        """
        res = super()._compute_domain(model_name, mode=mode)
        user = self.env.user
        group1 = "sales_team.group_sale_salesman"
        group2 = "sales_team_security.group_sale_team_manager"
        group3 = "sales_team.group_sale_salesman_all_leads"
        if model_name == "res.partner" and user.id != SUPERUSER_ID:
            if user.has_group(group1) and not user.has_group(group3):
                extra_domain = [
                    '|',
                    ('message_partner_ids', 'in', user.partner_id.ids),
                    '|',
                    ('id', '=', user.partner_id.id),
                ]
                if user.has_group(group2):
                    extra_domain += [
                        "|",
                        ("team_id", "=", user.sale_team_id.id),
                        ("team_id", "=", False),
                    ]
                else:
                    extra_domain += [
                        "|",
                        ("user_id", "=", user.id),
                        "&",
                        ("user_id", "=", False),
                        "|",
                        ("team_id", "=", False),
                        ("team_id", "=", user.sale_team_id.id),
                    ]
                extra_domain = expression.normalize_domain(extra_domain)
                res = expression.AND([extra_domain] + [res])
        return res
