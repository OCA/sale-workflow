# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    manufactured_for_partner_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="product_template_res_partner_rel",
        column1="product_template_id",
        column2="res_partner_id",
        domain=["|", ("customer_rank", ">", 0), ("is_company", "=", True)],
        string="Manufactured for",
    )
