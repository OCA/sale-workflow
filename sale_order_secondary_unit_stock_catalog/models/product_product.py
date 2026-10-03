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
        compute_sudo=False,
        help="""
            Shows available quantity in default sales secondary unit,
            only in is required in a Sales Order Catalog; otherwise it will
            return zero
        """,
    )
    has_sale_secondary_unit_qty_available = fields.Boolean(
        string="Has Quantity On Hand for Sale Secondary Unit",
        compute="_compute_sale_secondary_unit_qty_available",
        compute_sudo=False,
        help="""
            Technical field that helps to show/hide the secondary unit
            quantity available stock
        """,
    )

    @api.depends(
        "stock_move_ids.product_qty", "stock_move_ids.state", "stock_move_ids.quantity"
    )
    @api.depends_context(
        "lot_id",
        "owner_id",
        "package_id",
        "from_date",
        "to_date",
        "location",
        "warehouse",
        "allowed_company_ids",
        "product_catalog_order_model",
    )
    def _compute_sale_secondary_unit_qty_available(self):
        """
        Update quantity in default sales secondary unit, only if we are placed
        in a sale order product catalog, and only for those products that have
        such secondary unit defined
        """
        products_ssu = self.browse([])
        if self.env.context.get("product_catalog_order_model", False) == "sale.order":
            dp = self.env["decimal.precision"].precision_get("Product Unit of Measure")
            products_ssu = self.filtered(
                lambda product: product.sale_secondary_uom_id
                and product.sale_secondary_uom_id.factor > 0.0
                and product.sale_secondary_uom_id.dependency_type != "independent"
            )
            for product in products_ssu:
                ssu_qty_available = (
                    product.qty_available / product.sale_secondary_uom_id.factor
                )
                product.update(
                    {
                        "sale_secondary_unit_qty_available": ssu_qty_available,
                        "has_sale_secondary_unit_qty_available": not float_is_zero(
                            ssu_qty_available, precision_digits=dp
                        ),
                    }
                )
        (self - products_ssu).update(
            {
                "sale_secondary_unit_qty_available": 0.0,
                "has_sale_secondary_unit_qty_available": False,
            }
        )
