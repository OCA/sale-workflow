# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import datetime, time, timedelta

from psycopg2 import sql

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    cutoff_time_hms = fields.Char(
        compute="_compute_cutoff_time_hms", store=True, default="00:00"
    )
    cutoff_time_diff = fields.Integer(
        compute="_compute_cutoff_time_diff",
        search="_search_cutoff_time_diff",
        store=False,
    )
    expected_delivery_date = fields.Datetime(compute="_compute_expected_delivery_date")

    def _get_delays(self):
        self.ensure_one()
        sale_delays = self.move_lines.product_id.mapped("sale_delay")
        if sale_delays:
            # Depending on the move_type, customer_lead is either the smallest
            # or the biggest one among product's sale_delays.
            if self.move_type == "direct":
                min_delay = min(sale_delays)
                # As we cannot have negative delays
                customer_lead = max(min_delay, 0.0)
            else:
                max_delay = max(sale_delays)
                customer_lead = max(max_delay, 0.0)
        else:
            customer_lead = 0.0
        # Otherwise, this is the same than _get_delays() on sale_order_line
        security_lead = max(self.company_id.security_lead or 0.0, 0.0)
        workload = max(customer_lead - security_lead, 0.0)
        return customer_lead, security_lead, workload

    def _get_expected_expedition_date(self):
        """Retrieves the latest expedition date from date_deadline"""
        self.ensure_one()
        date_deadline = self.date_deadline
        if not date_deadline:
            return fields.Datetime.now()
        sale_line_model = self.env["sale.order.line"]
        delays = self._get_delays()
        calendar = self._get_warehouse_calendar()
        return sale_line_model._expedition_date_from_delivery_date(
            date_deadline - timedelta(days=7), # TODO: we don't know the start of the date range
            date_deadline,
            delays,
            calendar=calendar
        )

    def _get_warehouse_calendar(self):
        self.ensure_one()
        warehouse = self.location_id.get_warehouse()
        return warehouse.calendar2_id or None

    def _is_late_to_ship(self, next_expedition_date):
        self.ensure_one()
        expected_expedition_date = self._get_expected_expedition_date()
        return next_expedition_date.date() > expected_expedition_date.date()

    def _get_next_expedition_date(self, from_date):
        self.ensure_one()
        calendar = self._get_warehouse_calendar()
        if calendar:
            # plan_hours will return the same datetime if now is part of an attendance,
            # otherwise the beginning of the next one.
            # If the returned date is after the scheduled date, then we are late
            # to ship, and we need to postpone the delivery dates of the moves.
            return calendar.plan_hours(0, from_date, compute_leaves=True)
        else:
            return from_date

    def _get_delivery_date_from_expedition_date(
            self, next_expedition_date, partner, calendar, delays
        ):
        return self.env["sale.order.line"]._delivery_date_from_expedition_date(
            next_expedition_date, partner, calendar, delays
        )

    def _compute_expected_delivery_date(self):
        """Computes the expected delivery date.

        In some cases, the order expected_date and commitment_date
        can be in the past.
        e.g. when the current picking is a backorder.
        Also, we can have pickings that should be considered as backorders
        but where backorder_id is not set.
        e.g. If lines are added to a SO after it has been validated.
        In such case, we do not want to display those dates that are
        not valid for the current picking, and set the delivery_date
        as date_done + company.security_lead.
        We still try to keep this priority:
            commitment_date > expected_date > date_done > scheduled_date
        """
        now = fields.Datetime.now()
        sol_model = self.env["sale.order.line"]
        for record in self:
            delivery_date = record.date_deadline or record.date_done or now
            next_expedition_date = record._get_next_expedition_date(now)
            if record._is_late_to_ship(next_expedition_date):
                delays = record._get_delays()
                partner = record.partner_id
                calendar = record._get_warehouse_calendar()
                delivery_date = record._get_delivery_date_from_expedition_date(
                    next_expedition_date, partner, calendar, delays
                )
            record.expected_delivery_date = delivery_date

    @api.depends("location_id")
    def _compute_cutoff_time_diff(self):
        """Compute the stock.picking status in relation to warehouse cut-off time.

        Possible values are:
        -1 schedulled_date is in the past of yesterday's cutoff time
         0 scheduled_date is between yesterday and today's cuttoff
         1 scheduled_date is in the future of today's cutoff time

        """
        for record in self:
            warehouse = record.location_id.get_warehouse()
            hour, minute = warehouse._get_hour_min_from_value(warehouse.cutoff_time)
            today_cutoff = fields.Datetime.now().replace(
                hour=hour, minute=minute, second=0
            )
            yesterday_cutoff = fields.Datetime.subtract(today_cutoff, days=1)
            if record.scheduled_date < yesterday_cutoff:
                record.cutoff_time_diff = -1
            elif record.scheduled_date > today_cutoff:
                record.cutoff_time_diff = 1
            else:
                record.cutoff_time_diff = 0

    def _search_cutoff_time_diff(self, operator, value):
        if operator not in ("=", "!="):
            raise UserError(_("Unsupported search operator %s") % (operator,))
        today = fields.Datetime.now()
        yesterday = fields.Datetime.subtract(today, days=1)
        params = {
            "yesterday": fields.Date.to_string(yesterday),
            "today": fields.Date.to_string(today),
        }
        if value == -1:
            where = """
                scheduled_date < date(%(yesterday)s) + CAST(cutoff_time_hms AS Time)
            """
        elif value == 0:
            where = """
                scheduled_date >= date(%(yesterday)s) + CAST(cutoff_time_hms AS Time)
                AND
                scheduled_date <= date(%(today)s) + CAST(cutoff_time_hms AS Time)
            """
        elif value == 1:
            where = """
                scheduled_date > date(%(today)s) + CAST(cutoff_time_hms AS Time)
            """
        query = "SELECT id FROM stock_picking WHERE {}"
        # Disabling pylint because this is correct according to the doc
        # https://www.psycopg.org/docs/sql.html#module-psycopg2.sql
        self.env.cr.execute(  # pylint: disable=E8103
            sql.SQL(query).format(sql.SQL(where)), params
        )
        rows = self.env.cr.fetchall()
        picking_ids = [row[0] for row in rows]
        if operator == "=":
            new_operator = "in"
        else:
            new_operator = "not in"
        return [("id", new_operator, picking_ids)]

    @api.depends("location_id")
    def _compute_cutoff_time_hms(self):
        """Keep the time of the cutoff for the related warehouse

        In the format HH:MM which Postgres translate easily in Time format
        There is a limitation here if the cutoff time change on the warehouse
        record, it will not be propagated (But should not happen often).
        """
        for record in self:
            wh = record.location_id.get_warehouse()
            record.cutoff_time_hms = wh.float_to_time_repr(wh.cutoff_time)

    def _planned_delivery_date(self):
        res = super()._planned_delivery_date()
        sec_lead_time = self.company_id.security_lead
        if sec_lead_time:
            res += timedelta(days=sec_lead_time)
        return self.scheduled_date

    @api.onchange("scheduled_date")
    def _onchange_scheduled_date(self):
        res = super()._onchange_scheduled_date()
        if res and "warning" in res:
            sec_lead_time = self.company_id.security_lead
            if sec_lead_time:
                res["warning"]["message"] += (
                    _(
                        "\nConsidering the security lead time of %s days defined on "
                        "the company, the delivery will not match the partner time"
                        "windows preference."
                    )
                    % sec_lead_time
                )
        return res

    def get_cutoff_time(self):
        self.ensure_one()
        partner = self.partner_id
        wh = self.location_id.get_warehouse()
        delivery_preference = partner.order_delivery_cutoff_preference
        if delivery_preference == "warehouse_cutoff" and wh.apply_cutoff:
            cutoff = wh.get_cutoff_time()
        elif delivery_preference == "partner_cutoff":
            # Cutoff time is related to the warehouse, not to the customer.
            cutoff = partner.get_cutoff_time(tz=wh.tz)
        else:
            cutoff = {}
        return cutoff

    def _create_backorder(self):
        res = super()._create_backorder()
        sol_model = self.env["sale.order.line"]
        now = fields.Datetime.now()
        for picking in res:
            next_expedition_date = self._get_next_expedition_date(now)
            if picking._is_late_to_ship(next_expedition_date):
                for line in picking.move_lines:
                    dates = line._get_delivery_dates(from_date=now)
                    line.write(dates)
        return res
