# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-15 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval
from openerp.exceptions import except_orm

_logger = logging.getLogger(__name__)


class MrpPropertyFormula(orm.Model):
    _name = 'mrp.property.formula'
    _columns = {
        'name': fields.char('Name', size=128),
        'formula_text': fields.text(
            'Formula',
            help="Here you can write the formula using by python code"),
    }

    def compute_formula(self, local_dict):
        if ('result' not in self.formula_text):
            raise except_orm(
                _('Error'),
                _("Formula must contain 'result' variable"))
        safe_eval(self.formula_text, local_dict, mode="exec", nocopy=True)
        return local_dict['result']
