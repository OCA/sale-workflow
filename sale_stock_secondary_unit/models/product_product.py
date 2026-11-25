# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.tools import float_is_zero


class Product(models.Model):
    _inherit = "product.product"

    sale_secondary_unit_qty_available = fields.Float(
        string="Quantity On Hand for Sale Secondary Unit",
        compute="_compute_sale_secondary_unit_qty_available",
        digits="Product Unit of Measure",
        help="""
            Shows available quantity in default sales secondary unit,
            only in is required in a Sales Order Catalog; otherwise it will
            return zero
        """,
    )
    has_sale_secondary_unit_qty_available = fields.Boolean(
        string="Has Quantity On Hand for Sale Secondary Unit",
        compute="_compute_sale_secondary_unit_qty_available",
        help="""
            Technical field that helps to show/hide the secondary unit
            quantity available stock
        """,
    )

    @api.depends("qty_available", "sale_secondary_uom_id", "stock_secondary_uom_id")
    @api.depends_context(
        "lot_id",
        "owner_id",
        "package_id",
        "from_date",
        "to_date",
        "location",
        "warehouse_id",
        "allowed_company_ids",
        "is_storable",
        "product_catalog_order_model",
    )
    def _compute_sale_secondary_unit_qty_available(self):
        """
        Update quantity in default sales secondary unit, only if we are placed
        in a sale order product catalog
        """
        self.update(
            {
                "sale_secondary_unit_qty_available": 0.0,
                "has_sale_secondary_unit_qty_available": False,
            }
        )
        if self.env.context.get("product_catalog_order_model") != "sale.order":
            return
        res = self._get_sale_secondary_unit_qty_available_dict()
        for product in self:
            product.update(res.get(product.id, {}))

    def _get_sale_secondary_unit_qty_available_dict(self):
        dp = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        res = {}
        for product in self:
            secondary_uom = product.sale_secondary_uom_id
            if (
                not secondary_uom
                or secondary_uom == product.stock_secondary_uom_id
                or secondary_uom.factor <= 0.0
                or secondary_uom.dependency_type == "independent"
            ):
                continue
            qty_available = product.qty_available / secondary_uom.factor
            res[product.id] = {
                "sale_secondary_unit_qty_available": qty_available,
                "has_sale_secondary_unit_qty_available": not float_is_zero(
                    qty_available, precision_digits=dp
                ),
            }
        return res
