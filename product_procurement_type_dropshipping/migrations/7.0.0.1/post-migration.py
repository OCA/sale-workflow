# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

logger = logging.getLogger('openerp.upgrade')


def migrate(cr, version):
    logger.info('Migrating product_procurement_type_dropshipping')
    query = ("UPDATE product_template AS pt "
             "SET procurement_type=%(procurement_type)s "
             "FROM product_supplierinfo AS psi "
             "WHERE procure_method=%(procure_method)s "
             "  AND supply_method=%(supply_method)s "
             "  AND psi.product_id = pt.id "
             "  AND psi.direct_delivery_flag = true")
    fixes = [{'procurement_type': 'direct_delivery', 'procure_method': 'make_to_order', 'supply_method': 'buy'},
             ]
    for fix in fixes:
        cr.execute(query, fix)
