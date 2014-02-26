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
    logger.info('Migrating product_procurement_type')
    query = ("UPDATE product_template pt "
             "SET procurement_type=%(procurement_type)s "
             "WHERE procure_method=%(procure_method)s and supply_method=%(supply_method)s")
    fixes = [{'procurement_type': 'buy_stock', 'procure_method': 'make_to_stock', 'supply_method': 'buy'},
             {'procurement_type': 'buy_demand', 'procure_method': 'make_to_order', 'supply_method': 'buy'},
             {'procurement_type': 'produce_stock', 'procure_method': 'make_to_stock', 'supply_method': 'produce'},
             {'procurement_type': 'produce_demand', 'procure_method': 'make_to_order', 'supply_method': 'produce'},
             ]
    for fix in fixes:
        cr.execute(query, fix)
