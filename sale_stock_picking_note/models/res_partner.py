#  Copyright 2023 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner (models.Model):
    _inherit = 'res.partner'

    default_picking_note = fields.Text(
        string="Note for pickings",
        help="Default value for Picking Note in Sale Orders.",
    )
