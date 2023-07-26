# Copyright 2023 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_allowed_pricelist_ids = fields.Many2many(
        compute="_compute_partner_allowed_pricelist_ids",
        comodel_name="product.pricelist",
        help="Technical field used to show the allowed pricelists for the partner if "
        "the partner don't have allowed pricelists it shows all the pricelists.",
    )

    @api.depends("partner_id")
    def _compute_partner_allowed_pricelist_ids(self):
        for rec in self:
            if (
                rec.partner_id
                and rec.partner_id.commercial_partner_id.allowed_pricelist_ids
            ):
                rec.partner_allowed_pricelist_ids = (
                    rec.partner_id.commercial_partner_id.allowed_pricelist_ids
                )
            else:
                rec.partner_allowed_pricelist_ids = self.env[
                    "product.pricelist"
                ].search([])

    @api.constrains("pricelist_id")
    def _check_allowed_pricelist(self):
        for rec in self:
            if (
                self.company_id.use_partner_pricelist
                and rec.pricelist_id not in rec.partner_allowed_pricelist_ids
            ):
                raise ValidationError(
                    _("The selected Pricelist is not allowed for this Partner.")
                )
