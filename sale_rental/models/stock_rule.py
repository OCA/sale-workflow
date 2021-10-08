# Copyright 2014-2021 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016-2021 Sodexis (http://sodexis.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _push_prepare_move_copy_values(self, move_to_copy, new_date):
        """Inherit to write the end date of the rental on the return move"""
        res = super()._push_prepare_move_copy_values(move_to_copy, new_date)
        location_id = res.get("location_id", False)
        if (
            location_id
            and location_id == move_to_copy.warehouse_id.rental_out_location_id.id
            and move_to_copy.sale_line_id
            and move_to_copy.sale_line_id.rental_type == "new_rental"
        ):
            rental_end_date = move_to_copy.sale_line_id.end_date
            res["date"] = fields.Datetime.to_datetime(rental_end_date)
        return res
