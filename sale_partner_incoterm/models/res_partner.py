# Copyright 2015 Opener B.V. (<https://opener.am>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    sale_incoterm_id = fields.Many2one(
        string="Default Sales Incoterm",
        comodel_name="account.incoterms",
        help="The default incoterm for new sales orders for this customer.",
    )
