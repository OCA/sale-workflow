# -*- coding: utf-8 -*-
# Copyright 2018 Alex Comba - Agile Business Group
# Copyright 2016-2018 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, exceptions, _


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _prepare_mo_vals(self, bom):
        vals = super(ProcurementOrder, self)._prepare_mo_vals(bom)
        if self.group_id:
            sales = self.env['sale.order'].search(
                [('procurement_group_id', '=', self.group_id.id)])
            if len(sales) > 1:
                raise exceptions.ValidationError(
                    _('More than 1 sale order found for this group'))
            vals['sale_order_id'] = sales.id
        return vals
