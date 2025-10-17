# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    use_sale_confirmation_groups = fields.Boolean()
    sale_confirmation_group_ids = fields.Many2many(
        "res.groups",
        relation="res_company_2_res_groups_sales_confirm_rel",
        column1="company_id",
        column2="group_id",
    )
