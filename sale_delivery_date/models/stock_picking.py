# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import timedelta

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
        today = fields.Date.today()
        for record in self:
            delivery_date = False
            commitment_date = record.sale_id.commitment_date
            expected_date = record.sale_id.expected_date
            # If we commited to deliver on a given date, we never fall back
            # on the expected_date.
            # The reason for that is that we might have set and unrealistic
            # commitment_date at first.
            # In such case, it's normal to be late, and we do not want to postpone.
            if commitment_date:
                if commitment_date.date() >= today:
                    delivery_date = commitment_date
            elif expected_date and expected_date.date() >= today:
                delivery_date = expected_date
            if not delivery_date:
                date_done = record.date_done or record.scheduled_date
                sale_line_model = self.env["sale.order.line"]
                partner = self.partner_id
                warehouse = self.location_id.get_warehouse()
                delays = self._get_delays()
                delivery_date = sale_line_model._delivery_date_from_expedition_date(
                    date_done, partner, warehouse.calendar2_id, delays
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
        now = fields.Datetime.now()
        for picking in res:
            # If the scheduled_date is before the current datetime, then date_deadline
            # cannot be satisfied. Therefore, we need to recompute move's dates
            if picking.scheduled_date < now:
                for line in picking.move_lines:
                    dates = line._get_delivery_dates(from_date=now)
                    line.write(dates)
        return res
