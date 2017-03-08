# -*- coding: utf-8 -*-
#   Copyright (C) 2015 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    team_partner_invoice_id = fields.Many2one(
        comodel_name='res.partner', string='Final Partner for Invoicing',
        help="Select the final partner to invoice")
