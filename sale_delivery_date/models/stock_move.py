# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_delays(self):
        self.ensure_one()
        customer_lead = self.product_id.sale_delay
        security_lead = self.company_id.security_lead or 0.0
        workload = customer_lead - security_lead
        return customer_lead, security_lead, workload

    def _get_delivery_dates(self, from_date=None):
        """Returns the delivery dates, according to the from_date arg, or now(),
        if not set.
        """
        self.ensure_one()
        if not from_date:
            from_date = fields.Datetime.now()
        partner = self.picking_id.partner_id
        warehouse = self.picking_id.picking_type_id.warehouse_id
        calendar = warehouse.calendar_id
        customer_lead, security_lead, workload = self._get_delays()
        sale_line_model = self.env["sale.order.line"]
        workload_days = sale_line_model._delay_to_days(workload)
        # Those steps are the same as in sale_order_line.py,
        # in the `_prepare_procurement_values_no_commitment_date` method,
        # which means that we compute both date_planned and date_deadline based
        # on `from_date`:
        #   1) apply cutoff (partner or warehouse cutoff, depending on the config)
        #   2) apply the workload
        #   3) apply partner's time window to get the date deadline
        #   4) deduce security_lead and the workload to get the date planned
        date_planned = sale_line_model._apply_cutoff(from_date, partner, warehouse)
        date_planned = sale_line_model._apply_workload(
            date_planned, workload_days, calendar
        )
        date_deadline = sale_line_model._apply_delivery_window(
            date_planned, partner, security_lead, calendar
        )
        date_planned = sale_line_model._deduce_workload_and_security_lead(
            date_deadline, partner, warehouse, workload_days, security_lead
        )
        return {"date": date_planned, "date_deadline": date_deadline}
