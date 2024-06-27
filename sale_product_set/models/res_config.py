# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    archive_partner_product_sets = fields.Boolean(
        config_parameter="sale_product_set.archive_partner_product_sets",
        string="Sync product sets active state with partner",
        help="When a partner is archived or un-archived \
            its product sets are archived or un-archived as well.",
    )
