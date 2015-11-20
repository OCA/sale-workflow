# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
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

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('section_id')
    def section_id_set_section_id_default(self):
        self.payment_term = self.section_id.payment_term_id
        self.fiscal_position = self.section_id.fiscal_position_id
        self.pricelist_id = self.section_id.pricelist_id
        self.warehouse_id = self.section_id.warehouse_id
        self.project_id = self.section_id.account_analytic_id

    @api.onchange('user_id')
    def user_id_change_section_id(self):
        self.section_id = self.user_id.default_section_id
