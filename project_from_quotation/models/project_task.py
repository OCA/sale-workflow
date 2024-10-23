# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class Task(models.Model):
    _inherit = "project.task"

    quotation_line_id = fields.Many2one(
        comodel_name="sale.order.line",
    )
