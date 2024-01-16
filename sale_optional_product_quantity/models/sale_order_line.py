# Copyright 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model_create_multi
    def create(self, vals_list):
        optional_quantity_enabled = self.env.user.has_group(
            "product_optional_product_quantity.group_product_optional_quantity"
        )
        if not optional_quantity_enabled:
            return super().create(vals_list)
        res = super().create(vals_list)
        for line in res:
            for product_tmpl in line._get_optional_products():
                product = self.env["product.product"].search(
                    [("product_tmpl_id", "=", product_tmpl.id)]
                )[0]
                option = line.order_id._create_optional_line_if_not_exists(
                    product_tmpl,
                    product._get_tax_included_unit_price(
                        line.company_id,
                        line.order_id.currency_id,
                        line.order_id.date_order,
                        "sale",
                        fiscal_position=line.order_id.fiscal_position_id,
                        product_currency=line.currency_id,
                    ),
                )
                option._compute_quantity()
            if line._is_optional_product():
                line.order_id._create_optional_line_if_not_exists(
                    line.product_template_id, line.price_unit
                )
        return res

    @api.depends("product_template_id", "order_id.order_line")
    def _compute_product_uom_qty(self):
        optional_quantity_enabled = self.env.user.has_group(
            "product_optional_product_quantity.group_product_optional_quantity"
        )
        if not optional_quantity_enabled:
            return super()._compute_product_uom_qty()
        for line in self:
            order = line.order_id
            line_product_id = line.product_template_id.id
            order_lines = order.order_line.filtered(
                lambda x: line_product_id
                in (x.product_template_id.optional_product_ids.ids)
            )
            if not order_lines:
                line.product_uom_qty = line.product_uom_qty
                continue

            multiplier = sum(
                order_lines.mapped("product_template_id")
                .mapped("product_optional_line_ids")
                .filtered(lambda x: x.optional_product_tmpl_id.id == line_product_id)
                .mapped("quantity")
            )
            qty = sum(order_lines.mapped("product_uom_qty"))
            line.product_uom_qty = qty * multiplier

    def _is_optional_product(self):
        """
        Check if product is optional.

        Returns:
            bool: True if product is optional, False otherwise
        """
        self.ensure_one()
        return bool(
            self.env["product.template"].search_count(
                [("optional_product_ids", "in", self.product_template_id.id)]
            )
        )

    def _get_optional_products(self):
        """
        Get product.template recordset with product templates
        related to current line's product as optional products.

        Returns:
            product.template recordset: Optional products
        """
        self.ensure_one()
        return (
            self.env["product.optional.line"]
            .search([("product_tmpl_id", "=", self.product_template_id.id)])
            .mapped("optional_product_tmpl_id")
        )
