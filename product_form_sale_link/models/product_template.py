# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sale_lines_count = fields.Float(compute="_compute_sale_lines_count", string="Sold")

    @api.depends("product_variant_ids.sale_lines_count")
    def _compute_sale_lines_count(self):
        for product in self:
            product.sale_lines_count = sum(
                [
                    p.sale_lines_count
                    for p in product.with_context(active_test=False).product_variant_ids
                ]
            )
