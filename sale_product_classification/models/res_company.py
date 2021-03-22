# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_classification_a = fields.Monetary(
        string="Sales equal or above this amount",
        default=10000,
    )
    sale_classification_b = fields.Monetary(
        string="Sales equal or above this amount and below A",
        default=5000,
    )
    sale_classification_c = fields.Monetary(
        string="Sales equal or above this amount and below B",
        default=2500,
    )
    sale_classification_days_to_evaluate = fields.Integer(
        string="From the date the action is run, evalute these days",
        default=365,
    )
    sale_classification_days_to_ignore = fields.Integer(
        string="Ignore products newer than these days",
        help="If set, the products created in these date ranges will be "
             "ignored in the classification compute",
        default=0,
    )
