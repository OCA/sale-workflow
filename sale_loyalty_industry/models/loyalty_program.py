# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import fields, models


class LoyaltyProgram(models.Model):
    _inherit = "loyalty.program"

    industry_ids = fields.Many2many(
        "res.partner.industry",
        string="Industries",
        help="The loyalty program is applied in these industries.",
    )
