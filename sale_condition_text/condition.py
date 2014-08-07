# -*- coding: utf-8 -*-
#
#
# Copyright Camptocamp SA
#
#
from osv import osv, fields


class AccountConditionText(osv.osv):

    """add info condition in the invoice"""
    _name = "account.condition_text"
    _description = "Invoice condition text"

    _columns = {'name': fields.char('Condition', required=True, size=128),
                'type': fields.selection([('header', 'Header'),
                                          ('footer', 'Footer')],
                                         'type',
                                         required=True),
                'text': fields.text('text', translate=True, required=True)}

    def get_value(self, cursor, uid, cond_id, field_name, partner_id=False):
        if not cond_id:
            return {}
        part_obj = self.pool.get('res.partner')
        text = ''
        try:
            lang = part_obj.browse(cursor, uid, partner_id).lang
        except:
            lang = 'en_US'
        cond = self.browse(cursor, uid, cond_id, {'lang': lang})
        text = cond.text
        return {'value': {field_name: text}}


AccountConditionText()
