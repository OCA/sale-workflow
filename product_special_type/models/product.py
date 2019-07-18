# Copyright 2012 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    special_type = fields.selection([('discount', 'Global Discount'),
                                     ('advance', 'Advance'),
                                     ('delivery', 'Delivery Costs')],
                                    string='Special Type',
                                    help="""Special products will not be
                                    displayed on invoices printed reports
                                    but will be summed in the totals.""")

