# Copyright 2026 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    blanket_order_seq_number_from_draft = fields.Boolean(
        "Enable Blanket Order numbering from draft state", default=False
    )
