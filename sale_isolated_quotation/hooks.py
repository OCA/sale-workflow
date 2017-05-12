# -*- coding: utf-8 -*-
# © 2017 Ecosoft (ecosoft.co.th).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import ast
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    """ Set value for is_order on old records """
    cr.execute("""
        update sale_order
        set is_order = true
        where state not in ('draft', 'cancel')
    """)


def uninstall_hook(cr, registry):
    """ Restore sale.order action, remove context value """
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        for action_id in ['sale.action_quotations', 'sale.action_orders']:
            action = env.ref(action_id)
            ctx = ast.literal_eval(action.context)
            del ctx['is_order']
            dom = ast.literal_eval(action.domain)
            dom = [x for x in dom if x[0] != 'is_order']
            if action_id == 'sale.action_quotations':
                dom.append(('state', 'not in', ('draft', 'sent', 'cancel')))
            action.write({'context': ctx, 'domain': dom})
