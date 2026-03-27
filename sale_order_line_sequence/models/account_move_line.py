# Copyright 2023 Forgeflow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    related_so_sequence = fields.Char(
        string="SO Line Number",
        compute="_compute_related_so_sequence",
    )

    @api.depends("move_id.invoice_line_ids")
    def _compute_related_so_sequence(self):
        for rec in self:
            if (
                len(rec.move_id.line_ids.sale_line_ids.order_id) > 1
                or len(rec.sale_line_ids) > 1
            ):
                sequences = sorted(
                    set(
                        (sl.visible_sequence, sl.order_id.name)
                        for sl in rec.sale_line_ids
                    )
                )
                rec.related_so_sequence = ", ".join(
                    f"{seq[1]}/{seq[0]}" for seq in sequences
                )
            else:
                rec.related_so_sequence = str(rec.sale_line_ids.visible_sequence)
