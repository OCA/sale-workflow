# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

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
