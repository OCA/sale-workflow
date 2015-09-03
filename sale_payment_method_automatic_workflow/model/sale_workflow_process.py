# -*- coding: utf-8 -*-
###############################################################################
#
#    sale_automatic_workflow for OpenERP
#    Copyright 2015 Camptocamp SA (Alexandre Fayolle)
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
###############################################################################
from openerp import models, fields


class SaleWorkflowProcess(models.Model):
    _inherit = 'sale.workflow.process'

    autopay = fields.Boolean(
        help='if set, a payment will automatically be generated '
        'for the sale order.'
        )
