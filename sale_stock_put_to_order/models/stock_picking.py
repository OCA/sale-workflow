# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _get_pto_root_location(self):
        """Return the configured put-to-order root location."""
        self.ensure_one()
        dest = self.picking_type_id.default_location_dest_id
        return dest if dest and dest.is_pto else self.env["stock.location"]

    def _get_pto_source_products(self):
        """Return products relevant to PTO resolution.

        When a sale order is linked (via sale_line_id or procurement group),
        returns the full SO product list (including lines not yet delivered)
        so that bin selection considers the complete order context.
        Falls back to move products otherwise.
        """
        self.ensure_one()
        sale_orders = self.move_ids.mapped("sale_line_id.order_id")
        if not sale_orders and self.group_id:
            sale_orders = self.env["sale.order"].search(
                [("procurement_group_id", "=", self.group_id.id)], limit=1
            )
        source_sale_order = sale_orders[:1]
        if source_sale_order:
            return source_sale_order.order_line.mapped("product_id")
        return self.move_ids.product_id

    def _is_pto_location_valid(self, location, quants):
        """Check whether *location* can accept the products in *candidate_quants*."""
        location_qty = sum(quants.mapped("quantity"))
        return all(
            location._check_can_be_used(
                q.product_id, quantity=0, location_qty=location_qty
            )
            for q in quants
        )

    def _find_pto_dest_location_and_quants(self, excluded_locations=None):
        """Find a compatible PTO bin that already holds relevant products."""
        self.ensure_one()
        root = self._get_pto_root_location()
        locations = root._search_pto(
            excluded_locations=excluded_locations, company=self.company_id
        )
        products = self._get_pto_source_products()
        if not products or not locations:
            return
        quants = self.env["stock.quant"]._search_pto(locations, products)
        quants_by_location = defaultdict(lambda: self.env["stock.quant"])
        for quant in quants:
            quants_by_location[quant.location_id] |= quant
        for location in sorted(quants_by_location, key=lambda loc: loc.id):
            location_quants = quants_by_location[location]
            if self._is_pto_location_valid(location, location_quants):
                yield location, location_quants

    def _prepare_pto_bin_group_vals(self, location):
        """Build the bin group dict for a single *location*."""
        return {"name": location.name}

    def _get_pto_bin_groups(self):
        """Return ``{product_id: bin_group_vals}`` for valid PTO bins."""
        self.ensure_one()
        bin_groups = {}
        for location, quants in self._find_pto_dest_location_and_quants():
            vals = self._prepare_pto_bin_group_vals(location)
            for quant in quants:
                bin_groups.setdefault(quant.product_id.id, vals)
        return bin_groups
