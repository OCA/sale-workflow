# -*- coding: utf-8 -*-
# Copyright 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.translate import _


class SaleOrder(models.Model):
    _inherit = "sale.order"
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
                                     copy=False)
    unrevisioned_name = fields.Char('Order Reference',
                                    copy=True,
                                    readonly=True)
    active = fields.Boolean('Active',
                            default=True,
                            copy=True)

    _sql_constraints = [
        ('revision_unique',
         'unique(unrevisioned_name, revision_number, company_id)',
         'Order Reference and revision must be unique per Company.'),
    ]

    @api.returns('self', lambda value: value.id)
    @api.multi
    def copy(self, defaults=None):
        if not defaults:
            defaults = {}
        if self.env.context.get('new_sale_revision'):
            prev_name = self.name
            revno = self.revision_number
            self.write({'revision_number': revno + 1,
                        'name': '%s-%02d' % (self.unrevisioned_name,
                                             revno + 1)
                        })
            defaults.update({'name': prev_name,
                             'revision_number': revno,
                             'active': False,
                             'state': 'cancel',
                             'current_revision_id': self.id,
                             })
        return super(SaleOrder, self).copy(defaults)

    @api.model
    def create(self, values):
        if 'unrevisioned_name' not in values:
            if values.get('name', '/') == '/':
                seq = self.env['ir.sequence']
                values['name'] = seq.next_by_code('sale.order') or '/'
            values['unrevisioned_name'] = values['name']
        return super(SaleOrder, self).create(values)

    @api.multi
    def copy_quotation(self):
        # Adding Context
        self = self.with_context(new_sale_revision=True)

        # Getting the sale order form
        view_ref = self.env['ir.model.data'].get_object('sale',
                                                        'view_order_form')

        # Looping over sale order records
        for sale_order_rec in self:
            # Calling  Copy method
            copied_sale_rec = sale_order_rec.copy()

            msg = _('New revision created: %s') % sale_order_rec.name
            copied_sale_rec.message_post(body=msg)
            sale_order_rec.message_post(body=msg)

            action = {
                'type': 'ir.actions.act_window',
                'name': _('Sales Order'),
                'res_model': 'sale.order',
                'res_id': sale_order_rec.id,
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_ref.id,
                'target': 'current',
                'nodestroy': True,
            }

            # Returning the new sale order view with new record.
            return action
