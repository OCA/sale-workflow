# -*- coding: utf-8 -*-
#
#
#    Author: Nicolas Bessi
#    Copyright 2013-2014 Camptocamp SA
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
#
from openerp import models, fields, api


class BaseConditionTemplate(models.Model):

    """add info condition in the invoice"""
    _name = "base.condition_template"
    _description = "Base condition template text"

    name = fields.Char('Condition summary', required=True, size=128)
    position = fields.Selection([('before_lines', 'Before lines'),
                                 ('after_lines', 'After lines')],
                                'Postition',
                                required=True,
                                help="Position on document")
    text = fields.Html('Condition', translate=True, required=True)

    @api.multi
    def get_value(self, partner_id=False):
        self.ensure_one()
        try:
            lang = self.env['res.partner'].browse(partner_id).lang
        except:
            lang = 'en_US'
        return self.with_context({'lang': lang}).text
