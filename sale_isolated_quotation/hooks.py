# © 2017 Ecosoft (ecosoft.co.th).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import ast
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    """ Set value for order_sequence on old records """
    cr.execute("""
        update sale_order
        set order_sequence = true
        where state not in ('draft', 'cancel')
    """)


def uninstall_hook(cr, registry):
    """ Restore sale.order action, remove context value """
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        for action_id in ['sale.action_quotations', 'sale.action_orders']:
            action = env.ref(action_id)
            ctx = ast.literal_eval(action.context)
            del ctx['order_sequence']
            dom = ast.literal_eval(action.domain)
            dom = [x for x in dom if x[0] != 'order_sequence']
            if action_id == 'sale.action_quotations':
                dom.append(('state', 'not in', ('draft', 'sent', 'cancel')))
            action.write({'context': ctx, 'domain': dom})
