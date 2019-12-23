# Copyright 2015 Anybox S.A.S
# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ProductSet(models.Model):
    _name = "product.set"
    _description = "Product set"

    name = fields.Char(help="Product set name", required=True)
    active = fields.Boolean(string="Active", default=True)
    ref = fields.Char(
        string="Internal Reference", help="Product set internal reference", copy=False
    )
    set_line_ids = fields.One2many(
        "product.set.line", "product_set_id", string="Products"
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.user.company_id,
        ondelete="cascade",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        required=False,
        ondelete="cascade",
        index=True,
        help="You can attache the set to a specific partner "
        "or no one. If you don't specify one, "
        "it's going to be available for all of them.",
    )

    @api.multi
    def name_get(self):
        return [(rec.id, rec._name_get()) for rec in self]

    def _name_get(self):
        parts = []
        if self.ref:
            parts.append("[%s]" % self.ref)
        parts.append(self.name)
        if self.partner_id:
            parts.append("@ %s" % self.partner_id.name)
        return " ".join(parts)
