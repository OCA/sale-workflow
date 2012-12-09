# -*- encoding: utf-8 -*-
###############################################################################
#
#   sale_tax_inc_exc for OpenERP
#   Copyright (C) 2011-TODAY Akretion <http://www.akretion.com>. All Rights Reserved
#     @author Sébastien BEAU <sebastien.beau@akretion.com>
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import fields
from openerp.osv.orm import Model
import decimal_precision as dp
from tools.translate import _
from invoice_sale import InvoiceSale, InvoiceSaleLine


class account_invoice(InvoiceSale):
    _inherit = "account.invoice"

    _columns = {
        'tax_inc' : fields.boolean('Tax Inc', help="Tic the box if you want to use unit price in taxe include"),
    }
