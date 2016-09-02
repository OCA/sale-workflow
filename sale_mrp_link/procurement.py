# -*- coding: utf-8 -*-
##############################################################################
#
#  License AGPL version 3 or later
#  See license in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
#
##############################################################################

from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _prepare_mo_vals(self, procurement):
        vals = super(ProcurementOrder, self)._prepare_mo_vals(procurement)
        if procurement.group_id:
            sales = self.env['sale.order'].search(
                [('procurement_group_id', '=', self.group_id.id)])
            if len(sales) > 1:
                raise exceptions.ValidationError(
                    _("More than 1 sale order found for this group"))
            vals['sale_order_id'] = sales.id
        return vals
