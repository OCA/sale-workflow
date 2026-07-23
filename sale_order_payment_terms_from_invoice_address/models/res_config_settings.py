# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    compute_so_payment_terms_from_partner_invoice = fields.Boolean(
        string="Compute Sale Order Payment Terms from Invoice Address",
        help="If checked, the 'payment terms' on sale orders will be "
        "based on the payment terms of the invoice partner ('invoice address') "
        "instead of the base partner of the sale order ('customer')",
        config_parameter="sale_order_payment_terms_from_invoice_address."
        "compute_so_payment_terms_from_partner_invoice",
    )
