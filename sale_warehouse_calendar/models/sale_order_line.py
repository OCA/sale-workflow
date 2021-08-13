# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import timedelta

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _delay_to_days(self, number_of_days):
        """Converts a delay to a number of days."""
        return number_of_days + 1

    def _get_delays(self):
        # customer_lead is security_lead + workload, as explained on the field
        customer_lead = self.customer_lead or 0.0
        security_lead = self.company_id.security_lead or 0.0
        workload = customer_lead - security_lead
        return customer_lead, security_lead, workload

    def _expected_date(self):
        # Computes the expected date with respect to the WH calendar, if any.
        expected_date = super()._expected_date()
        return self._sale_warehouse_calendar_expected_date(expected_date)

    def _sale_warehouse_calendar_expected_date(self, expected_date):
        calendar = self.order_id.warehouse_id.calendar_id
        if calendar:
            customer_lead, security_lead, workload = self._get_delays()
            td_customer_lead = timedelta(days=customer_lead)
            td_security_lead = timedelta(days=security_lead)
            # plan_days() expect a number of days instead of a delay
            workload_days = self._delay_to_days(workload)
            # Remove customer_lead added to order_date in sale_stock
            expected_date -= td_customer_lead
            # Add the workload, with respect to the wh calendar
            expected_date = calendar.plan_days(
                workload_days, expected_date, compute_leaves=True
            )
            # add back the security lead
            expected_date += td_security_lead
        return expected_date

    def _prepare_procurement_values(self, group_id=False):
        res = super()._prepare_procurement_values(group_id=group_id)
        return self._sale_warehouse_calendar_prepare_procurement_values(res)

    def _sale_warehouse_calendar_prepare_procurement_values(self, res):
        date_planned = res.get("date_planned")
        calendar = self.order_id.warehouse_id.calendar_id
        if date_planned and calendar:
            customer_lead, security_lead, workload = self._get_delays()
            # plan_days() expect a number of days instead of a delay
            workload_days = self._delay_to_days(workload)
            td_workload = timedelta(days=workload)
            # Remove the workload that has been added by odoo
            date_planned -= td_workload
            # Add the workload, with respect to the wh calendar
            res["date_planned"] = calendar.plan_days(
                workload_days, date_planned, compute_leaves=True
            )
        return res
