# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import fields, models


class SaleOrderLine(models.Model):
    """Extend to add forced_reward_line field and override unlink."""

    _inherit = "sale.order.line"

    forced_reward_line = fields.Boolean(
        help="Tech field to cleanup automatically created lines"
    )

    def _get_discount_data_to_remove(self):
        data = defaultdict(dict)
        lines_to_remove = SaleOrderLine = self.env[self._name]
        SaleCouponProgram = self.env["sale.coupon.program"]
        for line in self:
            program = SaleCouponProgram.search(
                [
                    ("reward_type", "=", "product"),
                    ("reward_product_id", "=", line.product_id.id),
                ]
            )
            if not program:
                continue
            order = line.order_id
            # Picking from related order, because it is possible to
            # remove order lines from different orders at once.
            order_lines = order.order_line
            lines_to_remove |= order_lines.filtered(
                lambda r: r.product_id == program.discount_line_product_id
            )
            order_data = data[order.id]
            order_data.setdefault("lines", SaleOrderLine)
            order_data.setdefault("programs", SaleCouponProgram)
            order_data["lines"] |= lines_to_remove
            order_data["programs"] |= program
        return data

    def _collect_discount_lines_and_remove_programs(self):
        lines = self.env[self._name]
        data = self._get_discount_data_to_remove()
        SaleOrder = self.env["sale.order"]
        for order_id, data in data.items():
            lines |= data["lines"]
            programs = data["programs"]
            order = SaleOrder.browse(order_id)
            order.no_code_promo_program_ids -= programs
            order.code_promo_program_id -= programs
        return lines

    def unlink(self):
        """Override to unlink disc lines when reward ones are unlinked.

        Also removes related sale.coupon.program records.
        """
        if not self._context.get("discount_data_removed"):
            self |= self._collect_discount_lines_and_remove_programs()
        res = super(SaleOrderLine, self).unlink()
        return res
