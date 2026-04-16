# © 2025 OBS Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from collections import defaultdict

from odoo import fields, models

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _find_origin_sale_order(self):
        """Find the originating sale order for this MO.

        Prefer the procurement group link (most reliable), fall back to
        the move destinations, and finally to the origin name split on
        commas for legacy/manual origins.
        """
        self.ensure_one()
        SaleOrder = self.env["sale.order"]
        # 1. Via procurement group
        if self.procurement_group_id and self.procurement_group_id.sale_id:
            return self.procurement_group_id.sale_id
        # 2. Via downstream moves -> sale line
        sale_lines = self.move_finished_ids.move_dest_ids.sale_line_id
        if not sale_lines:
            sale_lines = self.move_dest_ids.sale_line_id
        if sale_lines:
            return sale_lines.order_id[:1]
        # 3. Fallback: parse comma-separated origin
        if self.origin:
            names = [n.strip() for n in self.origin.split(",") if n.strip()]
            if names:
                return SaleOrder.search([("name", "in", names)], limit=1)
        return SaleOrder

    def _get_sibling_mrp_productions(self, sale_order):
        """Return all MOs (including self) linked to the given sale order.

        Used to aggregate consumption across multiple MOs that share the
        same sale origin, ensuring idempotent updates to the SO.
        """
        self.ensure_one()
        MrpProduction = self.env["mrp.production"]
        siblings = MrpProduction
        if sale_order.procurement_group_id:
            siblings = MrpProduction.search(
                [("procurement_group_id", "=", sale_order.procurement_group_id.id)]
            )
        # Also match by origin as a fallback for MOs created manually
        # without being linked via procurement group.
        if sale_order.name:
            siblings |= MrpProduction.search([("origin", "=", sale_order.name)])
        # Always include self in case neither lookup finds it.
        return siblings | self

    @staticmethod
    def _get_move_qty_in_product_uom(move):
        """Return the move quantity converted to the product's default UoM."""
        product = move.product_id
        if move.product_uom and move.product_uom != product.uom_id:
            return move.product_uom._compute_quantity(move.quantity, product.uom_id)
        return move.quantity

    def action_add_consumed_components_to_sale(self):
        """Sync consumed components from done MOs to the originating SO.

        Aggregates consumption across all done MOs sharing the same sale
        origin. Idempotent: repeated calls produce the same result.
        """
        for mo in self:
            sale_order = mo._find_origin_sale_order()
            if not sale_order:
                _logger.info(
                    "No sale order found for MO %s (origin=%s)",
                    mo.name,
                    mo.origin,
                )
                continue

            # Aggregate consumption across all non-cancelled MOs linked to
            # this SO. The state='done' filter belongs in button_mark_done
            # (to decide when to trigger the sync), not here - this method
            # itself must work whenever it is called.
            consumption = defaultdict(float)
            sibling_mos = mo._get_sibling_mrp_productions(sale_order).filtered(
                lambda m: m.state != "cancel"
            )
            for sibling in sibling_mos:
                for move in sibling.move_raw_ids:
                    product = move.product_id
                    if not product.sale_ok or not move.quantity:
                        continue
                    consumption[product] += self._get_move_qty_in_product_uom(move)

            # Only match component lines we created earlier to avoid
            # writing to the original finished product line or unrelated
            # lines with the same product.
            so_line_map = {
                line.product_id.id: line
                for line in sale_order.order_line
                if line.is_mrp_component_line
            }

            for product, total_qty in consumption.items():
                if product.id in so_line_map:
                    so_line = so_line_map[product.id]
                    so_line.write(
                        {
                            "product_uom_qty": total_qty,
                            "qty_delivered_method": "manual",
                            "qty_delivered": total_qty,
                        }
                    )
                else:
                    date_order = sale_order.date_order or fields.Date.context_today(
                        sale_order
                    )
                    price = sale_order.pricelist_id._get_product_price(
                        product,
                        quantity=total_qty,
                        uom=product.uom_id,
                        date=date_order,
                        partner=sale_order.partner_id,
                    )
                    so_line = self.env["sale.order.line"].create(
                        {
                            "order_id": sale_order.id,
                            "product_id": product.id,
                            "product_uom_qty": total_qty,
                            "product_uom": product.uom_id.id,
                            "price_unit": price,
                            "name": product.display_name,
                            "qty_delivered_method": "manual",
                            "is_mrp_component_line": True,
                        }
                    )
                    so_line.qty_delivered = total_qty
                    _logger.info(
                        "Added product %s to sale order %s",
                        product.display_name,
                        sale_order.name,
                    )

    def button_mark_done(self):
        res = super().button_mark_done()
        # super().button_mark_done() may return a wizard action (immediate
        # production, backorder confirmation, consumption warning, ...) in
        # which case the MO is not actually done yet. Only sync when the
        # MO has truly reached the done state.
        for mo in self.filtered(lambda m: m.state == "done"):
            mo.action_add_consumed_components_to_sale()
        return res
