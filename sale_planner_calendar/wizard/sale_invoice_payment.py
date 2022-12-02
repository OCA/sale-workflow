# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleInvoicePaymentWiz(models.TransientModel):
    _inherit = "sale.invoice.payment.wiz"

    sale_planner_calendar_event_id = fields.Many2one(
        comodel_name="sale.planner.calendar.event"
    )

    def _prepare_sheet_line_values(self, invoice, amount_pay):
        values = super()._prepare_sheet_line_values(invoice, amount_pay)
        values.update(
            {"sale_planner_calendar_event_id": self.sale_planner_calendar_event_id.id}
        )
        return values
