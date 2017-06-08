# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services, S.L. -
# Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    partner_contact_id = fields.Many2one(
            'res.partner', 'Contact person', readonly=True,
            states={'draft': [('readonly', False)],
                    'sent': [('readonly', False)]},
            help="Contact person of the customer for this quotation "
                 "sales order.")
