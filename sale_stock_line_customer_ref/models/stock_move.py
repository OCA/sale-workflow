# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    customer_ref_sale_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        compute="_compute_customer_ref_sale_line_id",
        string="Sale Line With Customer Ref.",
        store=True,
        index=True,
    )
    customer_ref = fields.Char(compute="_compute_customer_ref", store=True)

    @api.depends("sale_line_id.customer_ref", "move_dest_ids.sale_line_id")
    def _compute_customer_ref_sale_line_id(self):
        for move in self:
            sale_line = move._get_customer_ref_sale_line()
            move.customer_ref_sale_line_id = sale_line

    @api.depends("customer_ref_sale_line_id.customer_ref")
    def _compute_customer_ref(self):
        for move in self:
            move.customer_ref = move.customer_ref_sale_line_id.customer_ref

    def _get_customer_ref_sale_line(self):
        """Return the SO line with a customer ref. from the ship move."""
        self.ensure_one()
        if self.sale_line_id.customer_ref:
            return self.sale_line_id
        # Search in the destination moves recursively until we find a SO line
        moves_dest = self.move_dest_ids
        move_seen_ids = set(moves_dest.ids)
        while moves_dest:
            for move_dest in moves_dest:
                # As soon as the SO line has a customer reference, we break.
                # That means for pick+pack moves we return the first SO line found.
                if move_dest.sale_line_id.customer_ref:
                    return move_dest.sale_line_id
            # Guard to avoid infinite loop. This should not happen.
            recursion_move_ids = move_seen_ids & set(moves_dest.move_dest_ids.ids)
            if recursion_move_ids:
                break
            moves_dest = moves_dest.move_dest_ids
            move_seen_ids |= set(moves_dest.ids)
        return self.sale_line_id.browse()

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super()._prepare_merge_moves_distinct_fields()
        # While ship moves can't be merged together as they are coming from
        # different SO lines ('sale_line_id' is part of the merge-key in
        # 'sale_stock'), we allow only the merge of chained moves like
        # pick+pack based on the customer reference.
        distinct_fields.append("customer_ref")
        return distinct_fields

    @api.model
    def _prepare_merge_move_sort_method(self, move):
        move.ensure_one()
        keys_sorted = super()._prepare_merge_move_sort_method(move)
        keys_sorted.append(move.customer_ref)
        return keys_sorted
