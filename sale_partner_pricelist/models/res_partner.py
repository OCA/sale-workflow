# Copyright 2023 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import threading

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartnerr(models.Model):
    _inherit = "res.partner"

    allowed_pricelist_ids = fields.Many2many(
        comodel_name="product.pricelist",
        copy=False,
        string="Allowed Pricelists",
    )

    @api.constrains("property_product_pricelist")
    def _check_allowed_pricelist(self):
        test_mode = self.env.registry.in_test_mode() or getattr(
            threading.current_thread(), "testing", False
        )
        for partner in self:
            if test_mode and not self._context.get("test_enable", False):
                continue

            if not partner.is_company:
                continue

            if (
                partner.property_product_pricelist
                and partner.property_product_pricelist
                not in partner.allowed_pricelist_ids
            ):
                raise ValidationError(
                    _("The selected Pricelist is not allowed for this Partner.")
                )
