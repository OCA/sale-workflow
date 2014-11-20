# -*- coding: utf-8 -*-
###############################################################################
#
#   sale_automatic_workflow for OpenERP
#   Copyright (C) 2011-TODAY Akretion <http://www.akretion.com>.
#     All Rights Reserved
#     @author Sébastien BEAU <sebastien.beau@akretion.com>
#   Copyright Camptocamp SA 2013 (Guewen Baconnier)
#
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
from openerp import models, fields


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    workflow_process_id = fields.Many2one(comodel_name='sale.workflow.process',
                                          string='Sale Workflow Process')
    # TODO propose a merge to add this field by default in acount module
    sale_ids = fields.Many2many(comodel_name='sale.order',
                                relation='sale_order_invoice_rel',
                                column1='invoice_id',
                                column2='order_id',
                                string='Sale Orders')
