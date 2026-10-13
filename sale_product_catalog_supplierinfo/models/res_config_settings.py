# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    catalog_show_vendor = fields.Boolean(
        string="Show the vendor on the catalog cards",
        config_parameter="sale_product_catalog_supplierinfo.catalog_show_vendor",
        help="Show the vendor name on the vendor cards of the product catalog. "
        "When unchecked, the cards show 'On order' instead.",
    )
