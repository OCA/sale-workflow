# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    @api.constrains('delivery_block_id')
    def _check_not_auto_done(self):
        if self.delivery_block_id and self.env['ir.values'].get_default(
                'sale.config.settings', 'auto_done_setting'):
            raise UserError(
                _('You cannot block a sale order with "auto_done_setting" '
                  'active.'))

    delivery_block_id = fields.Many2one(
        comodel_name='sale.delivery.block.reason',
        string='Delivery Block Reason', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """Add the 'Default Delivery Block Reason' if set in the partner."""
        res = super(SaleOrder, self).onchange_partner_id()
        for so in self:
            if so.partner_id.default_delivery_block:
                so.delivery_block_id = so.partner_id.default_delivery_block
        return res

    @api.multi
    def action_remove_delivery_block(self):
        """Remove the delivery block and create procurements as usual."""
        self.write({'delivery_block_id': False})
        for order in self:
            order.order_line._action_procurement_create()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _action_procurement_create(self):
        new_procs = self.env['procurement.order']
        # When module 'sale_procurement_group_by_line' is installed we do not
        # want to use this method but call super. See module
        # 'sale_delivery_block_proc_group_by_line'. This solves a inheritance
        # order issue.
        if 'group_by_line' in self.env.context:
            return super(SaleOrderLine, self)._action_procurement_create()
        for line in self:
            if not line.order_id.delivery_block_id:
                new_procs += super(SaleOrderLine,
                                   line)._action_procurement_create()
        return new_procs
