# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    show_client_order_ref_sale = fields.Boolean(
        related="company_id.show_client_order_ref_sale", readonly=False
    )
    show_client_order_ref_invoice = fields.Boolean(
        related="company_id.show_client_order_ref_invoice", readonly=False
    )
    client_order_ref_in_invoice_line_desc = fields.Boolean(
        related="company_id.client_order_ref_in_invoice_line_desc",
        readonly=False,
    )
    so_line_client_ref_policy = fields.Selection(
        related="company_id.so_line_client_ref_policy", readonly=False
    )
