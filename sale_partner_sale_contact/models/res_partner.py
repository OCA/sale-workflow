# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_contact_invoice_ids = fields.One2many(
        "account.move", "sale_contact_partner_id"
    )
    sale_contact_sale_ids = fields.One2many("sale.order", "sale_contact_partner_id")
