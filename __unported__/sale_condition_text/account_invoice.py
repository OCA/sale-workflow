# -*- coding: utf-8 -*-
#
#
# Copyright Camptocamp SA
#
#
from osv import osv, fields


class AccountInvoice(osv.osv):

    """Add text condition"""

    _inherit = "account.invoice"
    _columns = {
        'text_condition1': fields.many2one('account.condition_text', 'Header'),
        'text_condition2': fields.many2one('account.condition_text', 'Footer'),
        'note1': fields.text('Header'),
        'note2': fields.text('Footer')}

    def set_condition(
        self, cursor, uid, inv_id, cond_id, field_name, partner_id
    ):
        cond_obj = self.pool.get('account.condition_text')
        return cond_obj.get_value(cursor, uid, cond_id, field_name, partner_id)

AccountInvoice()
