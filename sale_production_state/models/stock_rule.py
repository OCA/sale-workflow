# Copyright 2021 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_mo_vals(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        company_id,
        values,
        bom,
    ):
        mo_vals = super()._prepare_mo_vals(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
            bom,
        )
        moves = values.get("move_dest_ids")
        line_ids = moves.sale_line_id
        while moves.move_dest_ids:
            moves = moves.move_dest_ids
            line_ids |= moves.sale_line_id
        mo_vals["sale_line_ids"] = line_ids and [(4, x.id) for x in line_ids] or False
        return mo_vals
