# -*- coding: utf-8 -*-
###############################################################################
#
#   sale_automatic_workflow for OpenERP
#   Copyright (C) 2011-TODAY Akretion <http://www.akretion.com>.
#     All Rights Reserved
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
from openerp import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    workflow_process_id = fields.Many2one(comodel_name='sale.workflow.process',
                                          string='Sale Workflow Process')

    def _create_invoice_from_picking(self, cr, uid, picking, vals,
                                     context=None):
        vals['workflow_process_id'] = picking.workflow_process_id.id
        if picking.workflow_process_id.invoice_date_is_order_date:
            vals['date_invoice'] = picking.sale_id.date_order

        _super = super(stock_picking, self)
        return _super._prepare_invoice(cr, uid, picking, vals, context=context)

    @api.multi
    def validate_picking(self):
        self.force_assign()
        self.do_transfer()
        return True
