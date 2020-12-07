# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    def _prepare_procurement_values_time_windows(self, date_planned):
        new_date_planned = super()._prepare_procurement_values_time_windows(
            date_planned
        )
        if new_date_planned:
            # if we have a new datetime proposed by a delivery time window,
            # apply the warehouse/partner cutoff time
            cutoff_datetime = self._prepare_procurement_values_cutoff_time(
                new_date_planned,
                # the correct day has already been computed, only change
                # the cut-off time
                keep_same_day=True,
            )
            if cutoff_datetime:
                return cutoff_datetime
        return new_date_planned
