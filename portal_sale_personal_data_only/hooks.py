# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry, vals=None):
    """Archive the ir.rules we want to override"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref('sale.sale_order_rule_portal').active = False
    env.ref('sale.sale_order_line_rule_portal').active = False
    env.ref('account.account_invoice_rule_portal').active = False
    env.ref('account.account_invoice_line_rule_portal').active = False


def uninstall_hook(cr, registry, vals=None):
    """Unarchive the overriden ir.rules"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref('sale.sale_order_rule_portal').active = True
    env.ref('sale.sale_order_line_rule_portal').active = True
    env.ref('account.account_invoice_rule_portal').active = True
    env.ref('account.account_invoice_line_rule_portal').active = True
