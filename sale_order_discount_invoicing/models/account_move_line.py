# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    discount_split_by_sale_line_id = fields.Many2one("sale.order.line", copy=False)
    is_split_line = fields.Boolean()
    is_split_discount_line = fields.Boolean()

    @property
    def _split_lines_group_fields(self) -> tuple:
        return "move_id", "discount_split_by_sale_line_id", "quantity"

    def _get_split_line_group_key(self) -> tuple:
        self.ensure_one()
        fnames = self._split_lines_group_fields
        data = self.read(fnames, load=0)[0]
        # Returned tuple must be ordered like the grouping field names
        return tuple(data[f] for f in fnames)
