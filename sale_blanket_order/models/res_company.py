from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    blanket_order_seq_number_from_draft = fields.Boolean(
        "Enable Blanket Order numbering from draft state", default=False
    )
