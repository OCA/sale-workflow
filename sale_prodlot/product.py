# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
#
##############################################################################

from openerp import models, fields
from openerp.osv import orm, fields as oldfields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    track_from_sale = fields.Boolean(
        'Track Lots since Sales',
        help="Forces to specifiy a Serial Number for all "
             "lines containing this product since the confirm "
             "of the Sale Order"
    )
