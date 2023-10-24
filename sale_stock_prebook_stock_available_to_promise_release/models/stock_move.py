# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _previous_promised_qty_sql_moves_before_matches(self):
        match_sql = super()._previous_promised_qty_sql_moves_before_matches()
        res = """
        (
            {match_sql}
            OR
            COALESCE(m.used_for_sale_reservation, False) = COALESCE(move.need_release, False)
        )
        """.format(
            match_sql=match_sql
        )
        return res

    def _previous_promised_qty_sql_moves_no_release(self):
        sql_no_release = super()._previous_promised_qty_sql_moves_no_release()
        return f"""
        (
            {sql_no_release}
        )
        AND (
            m.used_for_sale_reservation IS false OR m.used_for_sale_reservation IS NULL
        )"""
