# -*- coding: utf-8 -*-
# Copyright (C) 2016  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, exceptions, _


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _prepare_mo_vals(self, procurement):
        vals = super(ProcurementOrder, self)._prepare_mo_vals(procurement)
        if procurement.group_id:
            sales = self.env['sale.order'].search(
                [('procurement_group_id', '=', procurement.group_id.id)])
            if len(sales) > 1:
                raise exceptions.ValidationError(
                    _("More than 1 sale order found for this group"))
            vals['sale_order_id'] = sales.id
        return vals
