# -*- coding: utf-8 -*-

from osv import fields, osv
from tools.translate import _
from openerp import SUPERUSER_ID

"""
* Pre-book stock while sale order is not yet confirmed.
    Create a stock move (without picking and procurement) to decrease virtual stock. That reservation gets updated with the sale order line.
    If a reservation is existing at order confirmation, use it in the generated picking.
"""

class sale_order(osv.osv):
    _inherit = "sale.order"

    _columns = {
        'date_validity': fields.date("Valid Until", help="Define date until when quotation is valid",
                                     readonly=True,
                                     states={
                                        'draft':[('readonly',False)],
                                        'sent':[('readonly',True)], #don't allow to modify validity date when quotation has been send
                                     },
                                     track_visibility='onchange',
                                     ),
    }

