# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class BlanketOrder(models.Model):
    _inherit = "sale.blanket.order"

    margin = fields.Float(compute="_compute_margin", store=True)
    margin_percent = fields.Float("Margin (%)", compute="_compute_margin", store=True)

    @api.depends("line_ids", "line_ids.margin", "amount_untaxed")
    def _compute_margin(self):
        if not all(self._ids):
            for blanket in self:
                blanket.margin = sum(blanket.line_ids.mapped("margin"))
                blanket.margin_percent = (
                    blanket.amount_untaxed and blanket.margin / blanket.amount_untaxed
                )
        else:
            self.env["sale.blanket.order.line"].flush(["margin"])
            # On batch records recomputation (e.g. at install), compute the margins
            # with a single read_group query for better performance.
            # This isn't done in an onchange environment because (part of) the data
            # may not be stored in database (new records or unsaved modifications).
            grouped_order_lines_data = self.env["sale.blanket.order.line"].read_group(
                [
                    ("order_id", "in", self.ids),
                ],
                ["margin", "order_id"],
                ["order_id"],
            )
            mapped_data = {
                m["order_id"][0]: m["margin"] for m in grouped_order_lines_data
            }
            for blanket in self:
                blanket.margin = mapped_data.get(blanket.id, 0.0)
                blanket.margin_percent = (
                    blanket.amount_untaxed and blanket.margin / blanket.amount_untaxed
                )
