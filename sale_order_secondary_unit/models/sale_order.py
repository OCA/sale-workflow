# Copyright 2018-2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.http import request


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _update_order_line_info(self, product_id, quantity, **kwargs):
        # When adding a product through the catalog, take its default sale
        # secondary unit of measure into account so the catalog quantity refers
        # to that secondary unit instead of the product one.
        product = self.env["product.product"].browse(product_id)
        secondary_uom = product.sale_secondary_uom_id
        if not secondary_uom or quantity <= 0:
            return super()._update_order_line_info(product_id, quantity, **kwargs)
        # The line is created/updated here instead of delegating to super()
        # because the secondary unit must already be on the line when the stock
        # rule is launched: on create for a confirmed order, and on the
        # product_uom_qty write that `sale_stock` watches to propagate a
        # quantity change. Letting super() set product_uom_qty first and
        # patching the secondary unit afterwards leaves the generated moves
        # with the secondary quantity as their product quantity and no
        # secondary unit at all.
        if request:
            request.update_context(catalog_skip_tracking=True)
        sol = self.order_line.filtered(lambda line: line.product_id.id == product_id)
        if sol:
            sol.write(
                {
                    "secondary_uom_id": secondary_uom.id,
                    "secondary_uom_qty": quantity,
                    # `sale_stock` only propagates a quantity change when
                    # product_uom_qty is in the written values, and
                    # `sale_stock_secondary_unit` expects both quantities in the
                    # same write to size the procurement delta.
                    "product_uom_qty": sol._secondary_qty_to_product_qty(
                        secondary_uom, quantity
                    ),
                }
            )
        else:
            vals = {
                "order_id": self.id,
                "product_id": product_id,
                "secondary_uom_id": secondary_uom.id,
                "secondary_uom_qty": quantity,
                "sequence": (
                    (self.order_line and self.order_line[-1].sequence + 1) or 10
                ),
            }
            # product_uom_qty must be set explicitly for dependent secondary
            # units. Relying on the compute chain fails at create: the
            # product_uom compute recomputes secondary_uom_qty from the
            # still-default product_uom_qty (1.0), and product_uom_qty then ends
            # up derived from that stale value instead of the requested
            # secondary quantity. Sizing it here mirrors the write branch and
            # keeps the generated stock moves in the primary unit.
            if secondary_uom.dependency_type != "independent":
                qty_base = quantity * secondary_uom.factor
                vals["product_uom_qty"] = product.uom_id._compute_quantity(
                    qty_base, product.uom_id
                )
            sol = self.env["sale.order.line"].create(vals)
        return sol._get_discounted_price()

    def _get_product_catalog_order_data(self, products, **kwargs):
        # Expose the unit name so the catalog card can show it next to the
        # quantity input for products not in the order yet: the default sale
        # secondary unit when defined, otherwise the unit of measure that will
        # actually be added to the order.
        res = super()._get_product_catalog_order_data(products, **kwargs)
        for product in products:
            if product.sale_secondary_uom_id:
                res[product.id]["uomToAdd"] = product.sale_secondary_uom_id.display_name
            else:
                res[product.id]["uomToAdd"] = product.uom_id.display_name
        return res


class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "product.secondary.unit.mixin"]
    _name = "sale.order.line"
    _secondary_unit_fields = {
        "qty_field": "product_uom_qty",
        "uom_field": "product_uom",
    }

    secondary_uom_unit_price = fields.Float(
        string="2nd unit price",
        digits="Product Price",
        compute="_compute_secondary_uom_unit_price",
    )

    product_uom_qty = fields.Float(copy=True)

    def _secondary_qty_to_product_qty(self, secondary_uom, secondary_qty):
        """Return the product_uom_qty matching ``secondary_qty`` of
        ``secondary_uom``, the way ``_compute_helper_target_field_qty`` would.
        """
        self.ensure_one()
        if secondary_uom.dependency_type == "independent":
            return self.product_uom_qty
        qty_base = secondary_qty * secondary_uom.factor
        return self.product_id.uom_id._compute_quantity(qty_base, self.product_uom)

    @api.depends(
        "display_type",
        "product_id",
        "product_packaging_qty",
        "secondary_uom_qty",
        "secondary_uom_id",
        "product_uom_qty",
    )
    def _compute_product_uom_qty(self):
        res = super()._compute_product_uom_qty()
        for line in self:
            line._compute_helper_target_field_qty()
        return res

    @api.depends("product_id")
    def _compute_product_uom(self):
        res = super()._compute_product_uom()
        for line in self:
            line._onchange_helper_product_uom_for_secondary()
        return res

    @api.onchange("product_id")
    def _onchange_product_id_warning(self):
        res = super()._onchange_product_id_warning()
        if self.product_id and not self.env.context.get("skip_secondary_uom_default"):
            self.secondary_uom_id = self.product_id.sale_secondary_uom_id
            if self.product_uom_qty == 1.0:
                self.secondary_uom_qty = 1.0
                self._onchange_helper_product_uom_for_secondary()
        return res

    def _get_product_catalog_lines_data(self, **kwargs):
        """Show the secondary unit quantity in the catalog when the line uses
        a secondary unit of measure, so it stays consistent with the quantity
        handled in ``SaleOrder._update_order_line_info``. When the line has no
        secondary unit, expose its unit of measure instead.
        """
        res = super()._get_product_catalog_lines_data(**kwargs)
        if len(self) == 1:
            if self.secondary_uom_id:
                res["quantity"] = self.secondary_uom_qty
                res["uomToAdd"] = self.secondary_uom_id.display_name
            else:
                res["uomToAdd"] = self.product_uom.display_name
        return res

    @api.depends("secondary_uom_qty", "product_uom_qty", "price_unit")
    def _compute_secondary_uom_unit_price(self):
        for line in self:
            if line.secondary_uom_id:
                try:
                    line.secondary_uom_unit_price = (
                        line.price_subtotal / line.secondary_uom_qty
                    )
                except ZeroDivisionError:
                    line.secondary_uom_unit_price = 0
            else:
                line.secondary_uom_unit_price = 0
