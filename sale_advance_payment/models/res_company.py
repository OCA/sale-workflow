# Copyright 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    allow_advance_overpayment = fields.Boolean(
        string="Allow Advance Payments Exceeding Order Amount",
        help="If checked, advance payments larger than the order amount will be "
        "allowed. Useful for e-commerce scenarios where tax calculations may "
        "differ between the store and Odoo.",
    )
