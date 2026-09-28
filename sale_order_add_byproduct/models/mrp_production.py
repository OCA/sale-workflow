# © 2025 OBS Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)

DEFAULT_BYPRODUCT_NOTE_TEMPLATE = "{product_name} (By-product from MO: {mo_name})"


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def button_mark_done(self):
        """
        Overrides the standard button_mark_done to also add by-products to the
        sale order.
        """
        res = super().button_mark_done()
        for mo in self.filtered(lambda m: m.state == "done"):
            mo._add_byproducts_to_sale_order()
        return res

    @api.model
    def _get_byproduct_note_template(self, company):
        return company.byproduct_note_template or DEFAULT_BYPRODUCT_NOTE_TEMPLATE

    def _get_sale_order_for_byproducts(self):
        self.ensure_one()
        sale_order = self.sale_line_id.order_id or self.procurement_group_id.sale_id
        if not sale_order and self.origin:
            sale_order = self.env["sale.order"].search(
                [("name", "=", self.origin)], limit=1
            )
        return sale_order

    def _get_byproduct_moves_to_add(self):
        """
        Return byproduct moves with their picked quantities as a list of
        (move, quantity) tuples. Only saleable products are considered.
        """
        result = []
        for byproduct_move in self.move_byproduct_ids:
            if not byproduct_move.product_id.sale_ok:
                continue
            picked_lines = byproduct_move.move_line_ids.filtered("picked")
            quantity = (
                sum(picked_lines.mapped("quantity"))
                if picked_lines
                else byproduct_move.quantity
            )
            if (
                float_compare(
                    quantity,
                    0.0,
                    precision_rounding=byproduct_move.product_uom.rounding,
                )
                > 0
            ):
                result.append((byproduct_move, quantity))
        return result

    def _prepare_byproduct_sale_order_line_values(
        self, sale_order, byproduct_move, quantity
    ):
        self.ensure_one()
        product = byproduct_move.product_id
        template = self._get_byproduct_note_template(self.company_id)
        note = template.replace("{product_name}", product.name or "").replace(
            "{mo_name}", self.name or ""
        )
        date_order = sale_order.date_order or fields.Date.context_today(sale_order)
        price = sale_order.pricelist_id._get_product_price(
            product,
            quantity=quantity,
            uom=product.uom_id,
            date=date_order,
            partner=sale_order.partner_id,
        )
        return {
            "order_id": sale_order.id,
            "product_id": product.id,
            "product_uom_qty": quantity,
            "product_uom": product.uom_id.id,
            "price_unit": price,
            "name": note,
            "is_mrp_byproduct_line": True,
        }

    def _add_byproducts_to_sale_order(self):
        """
        Adds produced by-products to the related Sale Order.
        If a Sale Order is found, it will either create new order lines
        or update existing ones for the by-products.
        """
        self.ensure_one()
        sale_order = self._get_sale_order_for_byproducts()
        if not sale_order:
            _logger.debug(
                "MRP Production %s: No associated Sale Order found for by-product "
                "transfer. Origin: %s, Procurement Group: %s",
                self.name,
                self.origin,
                self.procurement_group_id,
            )
            return

        create_values_list = []
        for byproduct_move, quantity in self._get_byproduct_moves_to_add():
            product = byproduct_move.product_id
            existing_line = sale_order.order_line.filtered(
                lambda line, p=product: line.product_id == p
                and line.is_mrp_byproduct_line
            )[:1]
            if existing_line:
                existing_line.product_uom_qty += quantity
                _logger.debug(
                    "MRP Production %s: Updated Sale Order Line for %s "
                    "(Qty: %s) on SO %s.",
                    self.name,
                    product.name,
                    quantity,
                    sale_order.name,
                )
            else:
                create_values_list.append(
                    self._prepare_byproduct_sale_order_line_values(
                        sale_order, byproduct_move, quantity
                    )
                )

        if create_values_list:
            self.env["sale.order.line"].create(create_values_list)
            _logger.debug(
                "MRP Production %s: Batch created %d new Sale Order Lines on SO %s.",
                self.name,
                len(create_values_list),
                sale_order.name,
            )
