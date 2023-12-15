# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models
from odoo.osv import expression


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_program_domain(self):
        base_expression = super()._get_program_domain()
        domain = expression.AND(
            [
                base_expression,
                [
                    "|",
                    "|",
                    ("industry_ids", "=", False),
                    ("industry_ids", "child_of", self.partner_id.industry_id.ids),
                    ("industry_ids", "parent_of", self.partner_id.industry_id.ids),
                ],
            ]
        )
        return domain
