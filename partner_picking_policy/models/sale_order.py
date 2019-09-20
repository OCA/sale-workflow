# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Inherit the onchange on partner_id to update the default value
        of the picking_policy (who depends on the customer).
        :return:
        """
        result = super(SaleOrder, self).onchange_partner_id()
        if self.partner_id:
            if self.partner_id.picking_policy:
                picking_policy = self.partner_id.picking_policy
            else:
                picking_policy = self.env['ir.values'].get_default(
                    'sale.order', 'picking_policy')
            self.picking_policy = picking_policy
        return result
