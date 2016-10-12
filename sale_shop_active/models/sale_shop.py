# -*- coding: utf-8 -*-
# © 2016 Thomas Rehn (initOS GmbH)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields


class SaleShop(orm.Model):
    _inherit = "sale.shop"

    _columns = {
        'active': fields.boolean(
            string='Active',
            help="The active field allows you to hide the shop"
                 " without removing it."
        )
    }

    _defaults = {
        'active': True,
    }
