# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _update_candidate_moves_list(self, candidate_moves_set):
        """
        We want to merge stock moves within the stock reference only
        """
        res = super()._update_candidate_moves_list(candidate_moves_set)
        if self.env.context.get("sale_group_by_line"):
            candidate_moves_set.add(self.sale_line_id.stock_reference_id.move_ids)
        return res
