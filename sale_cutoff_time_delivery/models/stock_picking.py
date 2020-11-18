# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
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
