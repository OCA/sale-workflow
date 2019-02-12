# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    so_double_validation = fields.Selection(
        [
            ('one_step', 'Confirm sale orders in one step'),
            ('two_step', 'Get 2 levels of approvals to confirm a sale order')
        ],
        string="Levels of Approvals",
        default='one_step',
        help="Provide a double validation mechanism for purchases"
    )

    so_double_validation_amount = fields.Monetary(
        string='Double validation amount',
        default=5000,
        help="Minimum amount for which a double validation is required"
    )
