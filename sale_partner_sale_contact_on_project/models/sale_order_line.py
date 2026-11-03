# Copyright 2026 OpenStudio SAS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _timesheet_create_project_prepare_values(self):
        """Add sale contact to project values."""
        values = super()._timesheet_create_project_prepare_values()
        if self.order_id.sale_contact_partner_id:
            values["sale_contact_partner_id"] = self.order_id.sale_contact_partner_id.id
        return values
