# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from contextlib import contextmanager

from odoo import models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    def write(self, vals):
        with self._manage_route_update(vals):
            return super().write(vals)

    @contextmanager
    def _manage_route_update(self, vals):
        changed_lines = None
        if "route_id" in vals:
            changed_lines = self.filtered(lambda l: l._should_update_route(vals))
            changed_lines.move_ids._action_cancel()
            changed_lines.move_ids.write({"sale_line_id": False})
        yield
        if changed_lines:
            changed_lines._action_launch_stock_rule()

    def _should_update_route(self, vals):
        return self.filtered(
            lambda l, route_id=vals["route_id"]: l.state == "sale"
            and l.route_id.id != route_id
            and l.product_id.type == "product"
        )
