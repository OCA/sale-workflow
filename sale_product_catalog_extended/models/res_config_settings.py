# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


def _catalog_field_selection(field_name):
    """Options of a catalog search panel field, including the ones other modules
    add to it."""

    def selection(self):
        field = self.env["product.product"]._fields[field_name]
        return field._description_selection(self.env)

    return selection


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    default_catalog_origin_data = fields.Selection(
        selection=_catalog_field_selection("catalog_origin_data"),
        string="Catalog origin",
        default_model="product.product",
        help="Cards shown by default in the product catalog of sale orders. "
        "Products when empty.",
    )
    default_catalog_last_sales = fields.Selection(
        selection=_catalog_field_selection("catalog_last_sales"),
        string="Catalog last sales",
        default_model="product.product",
        help="Show by default only the products sold to the customer, most "
        "frequently sold first.",
    )
    default_catalog_price_mode = fields.Selection(
        selection=_catalog_field_selection("catalog_price_mode"),
        string="Catalog price",
        default_model="product.product",
        help="Price shown by default in the product catalog. The pricelist price "
        "when empty.",
    )
    default_catalog_history_partner = fields.Selection(
        selection=_catalog_field_selection("catalog_history_partner"),
        string="Catalog history partner",
        default_model="product.product",
        help="Partner the sale history is matched against by default. The "
        "customer (commercial partner) when empty.",
    )
    catalog_show_history_partner = fields.Boolean(
        string="Show the catalog history partner",
        config_parameter="sale_product_catalog_extended.catalog_show_history_partner",
        help="Show the History section in the product catalog search panel. "
        "When hidden, the history partner default still applies.",
    )
    catalog_last_order_days = fields.Integer(
        string="Catalog last sales days",
        config_parameter="sale_product_catalog_extended.catalog_last_order_days",
        default=180,
        help="Days of sale history used by the last sales option and the last "
        "sale price.",
    )
    catalog_last_order_limit = fields.Integer(
        string="Catalog last sales limit",
        config_parameter="sale_product_catalog_extended.catalog_last_order_limit",
        help="Maximum number of products shown by the last sales option. "
        "No limit when 0.",
    )
