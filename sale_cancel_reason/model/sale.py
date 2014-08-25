# -*- coding: utf-8 -*-
#
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
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

from openerp import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    cancel_reason_id = fields.Many2one(
        'sale.order.cancel.reason',
        string="Reason for cancellation",
        readonly=True,
        ondelete="restrict")


class SaleOrderCancelReason(models.Model):
    _name = 'sale.order.cancel.reason'
    _description = 'Sale Order Cancel Reason'

    name = fields.Char('Reason', required=True, translate=True)
