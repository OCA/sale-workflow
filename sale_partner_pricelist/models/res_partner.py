# Copyright 2023 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    allowed_pricelist_ids = fields.Many2many(
        comodel_name="product.pricelist",
        copy=False,
        string="Allowed Pricelists",
        domain=lambda self: [("company_id", "in", (self.env.company.id, False))],
        help="If set, you can only use the selected pricelists for this partner in "
        "the sale order.",
    )

    @api.constrains("property_product_pricelist", "allowed_pricelist_ids")
    def _check_allowed_pricelist(self):
        for partner in self:
            if (
                self.env.company.use_partner_pricelist
                and partner.commercial_partner_id.allowed_pricelist_ids
                and partner.commercial_partner_id.property_product_pricelist
                and partner.commercial_partner_id.property_product_pricelist
                not in partner.commercial_partner_id.allowed_pricelist_ids
            ):
                raise ValidationError(
                    _(
                        "The selected Pricelist is not allowed for this Partner. "
                        "Please select one of the allowed pricelists."
                    )
                )
