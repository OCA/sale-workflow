# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import api, fields, models


class SaleOrderRecommendationLine(models.TransientModel):
    _inherit = "sale.order.recommendation.line"

    product_packaging_id = fields.Many2one(
        "product.packaging",
        string="Packaging",
        index=True,
        compute="_compute_product_packaging",
        store=True,
        readonly=False,
        domain="[('product_id', '=', product_id), ('sales', '=', True)]",
        help="Packaging used for selling this product.",
    )
    product_packaging_qty = fields.Float(
        "Packaging Qty.",
        compute="_compute_product_packaging",
        readonly=False,
        store=True,
        digits="Product Unit of Measure",
        help="Quantity of packagings to sell.",
    )

    @api.depends("product_id", "units_included", "sale_uom_id")
    def _compute_product_packaging(self):
        """Set the most appropriate packaging for sales."""
        for line in self:
            # Empty when no product is selected
            if not line.product_id:
                line.product_packaging_id = False
                continue
            sale_pkgs = line.product_id.packaging_ids.filtered_domain(
                [("sales", "=", True)]
            )
            # Set default if there are not units included
            if not line.units_included:
                line.product_packaging_id = (
                    line.sale_line_id.product_packaging_id
                    or sale_pkgs.filtered_domain([("sales", "=", True)])[:1]
                )
                line.product_packaging_qty = 0
                continue
            # When there are units, apply best packaging
            uom = line.sale_uom_id or self.product_id.uom_id
            matching_packaging = sale_pkgs._find_suitable_product_packaging(
                line.units_included, uom
            )
            line.product_packaging_id = matching_packaging
            # Compute packaging qty
            try:
                rounded_qty = matching_packaging._check_qty(line.units_included, uom)
                line.product_packaging_qty = rounded_qty / line.product_packaging_id.qty
            except ValueError:
                # No packaging found
                line.product_packaging_qty = 0

    @api.onchange("product_packaging_id", "product_packaging_qty")
    def _onchange_product_packaging(self):
        """Update units_included when packaging changes."""
        # Keep packaging values like the user sees them currently
        with self.env.protecting(
            [
                self._fields["product_packaging_id"],
                self._fields["product_packaging_qty"],
            ],
            self,
        ):
            for line in self:
                if line.product_packaging_id:
                    line.units_included = (
                        line.product_packaging_id.qty * line.product_packaging_qty
                    )

    def _prepare_packaging_line_form(self, line_form):
        """Prepare packaging info for sale order line."""
        try:
            line_form.product_packaging_id = self.product_packaging_id
        except (AssertionError, KeyError):
            # No access to packaging
            return
        if self.product_packaging_id:
            line_form.product_packaging_qty = self.product_packaging_qty

    def _prepare_update_so_line(self, line_form):
        """Update a sale order line with packaging info."""
        result = super()._prepare_update_so_line(line_form)
        self._prepare_packaging_line_form(line_form)
        return result

    def _prepare_new_so_line(self, line_form, sequence):
        """Prepare product packaging info for new sale order line."""
        result = super()._prepare_new_so_line(line_form, sequence)
        self._prepare_packaging_line_form(line_form)
        return result
