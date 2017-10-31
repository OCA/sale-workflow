# -*- coding: utf-8 -*-
# Copyright 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.translate import _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('current_revision_id', 'old_revision_ids')
    def _has_old_revisions(self):
        for sale_order in self:
            if sale_order.old_revision_ids:
                sale_order.has_old_revisions = True
            else:
                sale_order.has_old_revisions = False

    current_revision_id = fields.Many2one('sale.order',
                                          'Current revision',
                                          readonly=True,
                                          copy=True)
    old_revision_ids = fields.One2many('sale.order',
                                       'current_revision_id',
                                       'Old revisions',
                                       readonly=True,
                                       context={'active_test': False})
    revision_number = fields.Integer('Revision',
                                     copy=False,
                                     default=0)
    unrevisioned_name = fields.Char('Order Reference',
                                    copy=True,
                                    readonly=True)
    active = fields.Boolean('Active',
                            default=True)

    has_old_revisions = fields.Boolean('Has old revisions',
                                       compute=_has_old_revisions)

    _sql_constraints = [
        ('revision_unique',
         'unique(unrevisioned_name, revision_number, company_id)',
         'Order Reference and revision must be unique per Company.'),
    ]

    @api.returns('self', lambda value: value.id)
    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        if self.env.context.get('new_sale_revision'):

            new_rev_number = self.revision_number + 1
            default.update({
                'revision_number': new_rev_number,
                'unrevisioned_name': self.unrevisioned_name,
                'name': '%s-%02d' % (self.unrevisioned_name, new_rev_number),
                'old_revision_ids': [(4, self.id, False)],
            })
            new_revision = super(SaleOrder, self).copy(default)
            self.old_revision_ids.write({
                'current_revision_id': new_revision.id,
            })
            self.write({'active': False,
                        'state': 'cancel',
                        'current_revision_id': new_revision.id,
                        })
            return new_revision

        else:
            if default.get('name', '/') == '/':
                seq = self.env['ir.sequence']
                default['name'] = seq.next_by_code('sale.order') or '/'
                default['revision_number'] = 0
                default['unrevisioned_name'] = default['name']
            return super(SaleOrder, self).copy(default=default)

    @api.model
    def create(self, values):
        if 'unrevisioned_name' not in values:
            if values.get('name', '/') == '/':
                seq = self.env['ir.sequence']
                values['name'] = seq.next_by_code('sale.order') or '/'
            values['unrevisioned_name'] = values['name']
        return super(SaleOrder, self).create(values)

    @api.multi
    def create_revision(self):

        revision_ids = []
        # Looping over sale order records
        for sale_order_rec in self:
            # Calling  Copy method
            copied_sale_rec = sale_order_rec.with_context(
                new_sale_revision=True).copy()

            msg = _('New revision created: %s') % copied_sale_rec.name
            copied_sale_rec.message_post(body=msg)
            sale_order_rec.message_post(body=msg)

            revision_ids.append(copied_sale_rec.id)

        action = {
            'type': 'ir.actions.act_window',
            'name': _('New Sales Order Revisions'),
            'res_model': 'sale.order',
            'domain': "[('id', 'in', %s)]" % revision_ids,
            'auto_search': True,
            'views': [
                (self.env.ref('sale.view_quotation_tree').id, 'tree'),
                (self.env.ref('sale.view_order_form').id, 'form')],
            'target': 'current',
            'nodestroy': True,
        }

        # Returning the new sale order view with new record.
        return action
