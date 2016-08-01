# -*- coding: utf-8 -*-
# © initOS GmbH 2016
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api
from openerp.osv import fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def action_assign(self):
        for move in self:
            if move.picking_id:
                # Write dummy variable so that the state of the
                #  picking will be updated.
                move.picking_id.dummy_int_to_trigger_state_update = \
                    (move.picking_id.dummy_int_to_trigger_state_update + 1) % 2
                if self._context.get('payment_check', True) and \
                        move.picking_id.is_on_hold():
                    # Do not assign picking because it is on hold
                    return False
        return super(StockMove, self).action_assign()


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _state_get(self, cr, uid, ids, field_name, arg, context=None):
        res = super(StockPicking, self).\
            _state_get(cr, uid, ids, field_name, arg, context=context)
        pickings = self.browse(cr, uid, res.keys(), context=context)
        for picking in pickings:
            if res[picking.id] == 'confirmed' and picking.is_on_hold():
                res[picking.id] = 'hold'
        return res

    def _get_pickings(self, cr, uid, ids, context=None):
        # Method is copied from stock/stock.py.
        # Calling _get_pickings of `super(StockPicking, self)` doesn't work
        # because when the method is being called, `self` is a stock.move.
        res = set()
        for move in self.browse(cr, uid, ids, context=context):
            if move.picking_id:
                res.add(move.picking_id.id)
        return list(res)

    _columns = {
        'state': fields.function(
            _state_get,
            type="selection",
            copy=False,
            store={
                'stock.picking': (
                    lambda self, cr, uid, ids, ctx: ids,
                    ['move_type', 'dummy_int_to_trigger_state_update'], 20),
                'stock.move': (
                    _get_pickings,
                    ['state', 'picking_id', 'partially_available'], 20)},
            selection=[
                ('draft', 'Draft'),
                ('cancel', 'Cancelled'),
                ('waiting', 'Waiting Another Operation'),
                ('confirmed', 'Waiting Availability'),
                ('partially_available', 'Partially Available'),
                ('hold', 'Waiting For Payment'),
                ('assigned', 'Ready to Transfer'),
                ('done', 'Transferred'),
            ],
            string='Status',
            readonly=True,
            select=True,
            track_visibility='onchange',
            help="""
            * Draft: not confirmed yet and will not be
             scheduled until confirmed\n
            * Waiting Another Operation: waiting for another move to
             proceed before \n
             it becomes automatically available
             (e.g. in Make-To-Order flows)\n
            * Waiting Availability: still waiting for the availability
             of products\n
            * Waiting For Payment: waiting for the payment
             of the related sale order\n
            * Partially Available: some products are available and reserved\n
            * Ready to Transfer: products reserved,
             simply waiting for confirmation.\n
            * Transferred: has been processed,
             can't be modified or cancelled anymore\n
            * Cancelled: has been cancelled, can't be confirmed anymore"""
        ),
        # In an ideal world "On Hold" would be a computed field that depends on
        # the payment status of the sale order. Unfortunately the changes
        # to the v7-functional fields 'sale_id.invoiced' don't seem to be
        # propagated to the new api.depends mechanism. There we use this ugly
        # workaround that forces the re-computation of the state whenever
        # action_assign is called.
        'dummy_int_to_trigger_state_update': fields.integer(
            string='Dummy Integer (to trigger update of state field)'
        )
    }

    @api.multi
    def is_on_hold(self):
        """Returns True iff picking should be held because the
           corresponding order has not been paid yet."""
        self.ensure_one()
        if self.sale_id and self.sale_id.payment_method_id and\
                self.sale_id.payment_method_id.hold_picking_until_payment and\
                not self.sale_id.invoiced:
            return True
        return False

    @api.multi
    def action_assign_unpaid(self):
        self.with_context(payment_check=False).action_assign()
