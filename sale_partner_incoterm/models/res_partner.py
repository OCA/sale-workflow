# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Opener B.V. (<https://opener.am>)
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
from openerp import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    sale_incoterm_id = fields.Many2one(
        string='Default Sales Incoterm',
        comodel_name='stock.incoterms',
        help="The default incoterm for new sales orders for this customer.")
