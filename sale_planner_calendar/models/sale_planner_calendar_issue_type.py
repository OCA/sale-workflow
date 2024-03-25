# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleEventPlannerIssueType(models.Model):
    _name = "sale.planner.calendar.issue.type"
    _description = "Sale planner calendar issue type"

    name = fields.Char()
