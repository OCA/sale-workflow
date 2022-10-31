# © 2017 Ecosoft (ecosoft.co.th).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import ast

from odoo import SUPERUSER_ID, api

ACTIONS = (
    "sale.action_quotations_with_onboarding",
    "sale.action_orders",
)


def post_init_hook(cr, registry):
    """Set value for order_sequence on old records, stop updating sale
    order name."""
    cr.execute(
        """
        update sale_order
        set order_sequence = true
        where state not in ('draft', 'cancel')
    """
    )


def uninstall_hook(cr, registry):
    """Restore sale.order action, remove context value"""
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        for action_id in ACTIONS:
            action = env.ref(action_id)
            ctx = ast.literal_eval(action.context)
            _cleanup_ctx(ctx)
            dom = ast.literal_eval(action.domain or "{}")
            dom = [x for x in dom if x[0] != "order_sequence"]
            if action_id == "sale.action_orders":
                dom.append(("state", "not in", ("draft", "sent", "cancel")))
            else:
                ctx["search_default_my_quotation"] = True
            dom = list(set(dom))
            action.write({"context": ctx, "domain": dom})


def _cleanup_ctx(ctx):
    if "order_sequence" in ctx:
        del ctx["order_sequence"]
    if "default_order_sequence" in ctx:
        del ctx["default_order_sequence"]
