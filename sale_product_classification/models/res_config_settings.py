# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_classification_a = fields.Monetary(
        related="company_id.sale_classification_a",
        readonly=False,
    )
    sale_classification_b = fields.Monetary(
        related="company_id.sale_classification_b",
        readonly=False,
    )
    sale_classification_c = fields.Monetary(
        related="company_id.sale_classification_c",
        readonly=False,
    )
    sale_classification_days_to_evaluate = fields.Integer(
        related="company_id.sale_classification_days_to_evaluate",
        readonly=False,
    )
    sale_classification_days_to_ignore = fields.Integer(
        related="company_id.sale_classification_days_to_ignore",
        readonly=False,
    )
