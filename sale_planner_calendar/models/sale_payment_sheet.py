# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SalePaymentSheetLine(models.Model):
    _inherit = "sale.payment.sheet.line"

    sale_planner_calendar_event_id = fields.Many2one(
        comodel_name="sale.planner.calendar.event"
    )
