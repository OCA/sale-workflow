# Copyright 2015 Opener B.V. (<https://opener.am>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    sale_incoterm_address_id = fields.Many2one(
        comodel_name="res.partner",
        string="Default Sale Incoterm Address",
    )
