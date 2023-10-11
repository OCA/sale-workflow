from odoo import fields, models
from odoo.tools.safe_eval import datetime, safe_eval


class ResCompany(models.Model):
    _inherit = "res.company"

    general_discount_applicable_to = fields.Text(default="[]", required=True)

    def _get_general_discount_eval_domain(self):
        self.ensure_one()
        return safe_eval(
            self.general_discount_applicable_to,
            {
                "datetime": datetime,
                "context_today": datetime.datetime.now,
            },
        )
