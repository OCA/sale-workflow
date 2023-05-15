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
        return (max(customer_lead, 0.0), max(security_lead, 0.0), max(workload, 0.0))

    def _get_delivery_dates(self, from_date=None):
        """Returns the delivery dates, according to the from_date arg, or now(),
        if not set.
        """
        self.ensure_one()
        if not from_date:
            from_date = fields.Datetime.now()
        partner = self.picking_id.partner_id
        warehouse = self.location_id.get_warehouse()
        calendar = warehouse.calendar2_id
        delays = self._get_delays()
        cutoff = self.picking_id.get_cutoff_time()
        sale_line_model = self.env["sale.order.line"]
        # Those steps are the same as in sale_order_line.py,
        # in the `_prepare_procurement_values_no_commitment_date` method,
        # which means that we compute both date_planned and date_deadline based
        # on `from_date`:
        #   1) apply cutoff (partner or warehouse cutoff, depending on the config)
        #   2) apply the workload
        #   3) apply partner's time window to get the date deadline
        #   4) deduce security_lead and the workload to get the date planned
        res = {}
        earliest_expedition_date = sale_line_model._expedition_date_from_date_order(
            from_date, delays, calendar=calendar, cutoff=cutoff
        )
        delivery_date = sale_line_model._delivery_date_from_expedition_date(
            earliest_expedition_date, partner, calendar, delays
        )
        res["date_deadline"] = delivery_date
        expedition_date = sale_line_model._expedition_date_from_delivery_date(
            earliest_expedition_date, delivery_date, delays, calendar=calendar
        )
        preparation_date = sale_line_model._preparation_date_from_expedition_date(
            expedition_date, delays, calendar=calendar, cutoff=cutoff
        )
        res["date"] = preparation_date
        return res
