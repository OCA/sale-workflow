# -*- coding: utf-8 -*-
# Copyright 2014-2015 Serv. Tecnol. Av. (http://www.serviciosbaeza.com)
#                     Pedro M. Baeza Romero <pedro.baeza@serviciosbaeza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, exceptions, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def button_draft(self):
        # go from canceled state to draft state
        for order in self:
            if order.state != 'cancel':
                raise exceptions.Warning(
                    _("You can't back any order that it's not on cancel "
                      "state. Order: %s" % order.name))
            order.order_line.write({'state': 'draft'})
            order.procurement_group_id.sudo().unlink()
            for line in order.order_line:
                line.procurement_ids.sudo().unlink()
            order.write({'state': 'draft'})
            order.delete_workflow()
            order.create_workflow()
        return True
