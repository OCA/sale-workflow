# coding: utf-8
# Copyright 2016 Opener B.V. - Stefan Rijnhart
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


class SaleOrderMerge(models.TransientModel):
    _name = 'sale.order.merge'
    _description = 'Merge sale orders'

    sale_order = fields.Many2one(
        'sale.order', 'Merge into', required=True, readonly=True)
    mergeable = fields.Many2many(
        comodel_name='sale.order',
        related='sale_order.merge_with')
    to_merge = fields.Many2many(
        'sale.order', 'rel_sale_to_merge', 'sale_id', 'to_merge_id',
        'Orders to merge')

    @api.multi
    def merge_order_lines(self):
        self.sale_order.write({
            'order_line': [
                (4, line.id)
                for line in self.to_merge.mapped('order_line')
            ]})

    @api.multi
    def merge_invoices(self):
        """ Merge all draft invoices. For prepaid orders, the payment
        of the original invoice is leading to start the procurement, but
        there may still be other confirmed invoices. """
        target = self.env['account.invoice']
        other_inv = self.env['account.invoice']
        keep_inv = self.env['account.invoice']
        for invoice in (
                self.sale_order.invoice_ids +
                self.to_merge.mapped('invoice_ids')):
            if invoice.state == 'draft' and not invoice.internal_number:
                if target:
                    other_inv += invoice
                else:
                    target = invoice
            else:
                keep_inv += invoice
        if target:
            other_inv.mapped('invoice_line').write({'invoice_id': target.id})
            other_inv.mapped('tax_line').write({'invoice_id': target.id})
            other_inv.unlink()
            target.button_compute(set_total=True)

        for inv in target + keep_inv:
            self.sale_order.write({'invoice_ids': [(4, inv.id)]})
        self.to_merge.write({'invoice_ids': [(6, 0, [])]})

    @api.multi
    def _picking_can_merge(self, picking):
        return (picking.state not in ('done', 'cancel') and
                picking.location_dest_id.usage == 'customer')

    @api.multi
    def _get_picking_map_key(self, picking):
        return (picking.picking_type_id, picking.location_id,
                picking.location_dest_id, picking.partner_id)

    @api.multi
    def merge_pickings(self):
        """ Assign all pickings to the target sale order and merge any
        pending pickings """
        orders = self.sale_order + self.to_merge
        group = self.env['procurement.group']
        if self.sale_order.procurement_group_id:
            group = self.sale_order.procurement_group_id
        else:
            for order in self.to_merge:
                if order.procurement_group_id:
                    group = order.procurement_group_id
                    break
            else:
                return  # no group, no pickings
            self.sale_order.write({'procurement_group_id': group.id})
        other_groups = orders.mapped('procurement_group_id')
        self.env['stock.picking'].search(
            [('group_id', 'in', other_groups.ids)]).write(
                {'group_id': group.id})
        self.env['stock.move'].search(
            [('group_id', 'in', other_groups.ids)]).write(
                {'group_id': group.id})
        self.env['procurement.order'].search(
            [('group_id', 'in', other_groups.ids)]).write(
                {'group_id': group.id})
        pick_map = {}
        for picking in self.sale_order.picking_ids:
            if self._picking_can_merge(picking):
                key = self._get_picking_map_key(picking)
                if key not in pick_map:
                    pick_map[key] = self.env['stock.picking']
                pick_map[key] += picking
            else:
                picking.write({'origin': group.name})
        for pickings in pick_map.values():
            target = pickings[0]
            if len(pickings) > 1:
                pickings -= target
                pickings.mapped('move_lines').write({'picking_id': target.id})
                pickings.unlink()
            target.write({'origin': group.name})
        return True

    @api.multi
    def open_sale(self):
        self.ensure_one()
        return {
            'name': _('Merged sale order'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.sale_order.id,
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def merge(self):
        """
        If not all orders have the same policy:
            If not all confirmed orders have the same policy:
                raise
            Set the policy to the policy of the confirmed order(s)

        If there is one confirmed order, confirm all other orders. For
        prepaid orders, this will generate draft invoices.
        """
        self.ensure_one()
        orders = self.sale_order + self.to_merge
        create_picking = False
        reset_wait_invoice = False

        if not all(order.state in ('sent', 'draft') for order in orders):
            # Propagate the order policy from the confirmed to the draft
            # orders, as they may be different.
            drafts = orders.filtered(
                lambda o: o.state in ('sent', 'draft'))
            confirmed = orders - drafts
            order_policy = confirmed[0].order_policy
            if not all(o.order_policy == order_policy for o in confirmed):
                raise UserError(
                    _('Cannot merge these orders because their order '
                      'policies cannot be reconciled.'))

            # Flag if the main order's workflow needs to be tickled after
            # merging if it already has passed the point of picking or invoice
            # generation
            if (order_policy == 'prepaid' and
                    self.sale_order.picking_ids):
                create_picking = True
            if (order_policy == 'manual' and
                    self.sale_order.state == 'progress' and
                    (drafts or confirmed.filtered(
                        lambda o: o.state == 'manual'))):
                reset_wait_invoice = True

            # Propagate order policy across draft orders
            drafts.filtered(
                lambda o: o.order_policy != order_policy).write(
                    {'order_policy': order_policy})
            for draft in drafts:
                # confirm orders to align state and create invoices
                # and/or pickings
                draft.action_button_confirm()
            self.merge_invoices()
            self.merge_pickings()

        self.merge_order_lines()
        self.to_merge.delete_workflow()
        self.to_merge.create_workflow()
        self.to_merge.signal_workflow('cancel')
        if create_picking:
            self.sale_order.action_ship_create()
        if reset_wait_invoice:
            item = self.env['workflow.workitem'].sudo().search(
                [('act_id', 'in', (
                    self.env.ref('sale.act_invoice_end').id,
                    self.env.ref('sale.act_invoice').id)),
                 ('inst_id.res_id', '=', self.sale_order.id)])
            if item:
                item_vals = {
                    'act_id': self.env.ref('sale.act_wait_invoice').id}
                if item.subflow_id:
                    item_vals['subflow_id'] = False
                if item.state == 'running':
                    item_vals['state'] = 'active'
                item.write(item_vals)
            self.sale_order.write({'state': 'manual'})
        for order in self.to_merge:
            order.message_post(_('Merged into %s') % self.sale_order.name)
        self.sale_order.message_post(
            _('Order(s) %s merged into this one') % ','.join(
                self.to_merge.mapped('name')))
        return self.open_sale()
