# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    default_route = fields.Many2one(
        string='Default Route',
        comodel_name='stock.location.route',
        help="Define the default route type associated with a partner.")
