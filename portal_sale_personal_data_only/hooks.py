# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry, vals=None):
    """Archive the ir.rules we want to override"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref('portal_sale.portal_sale_order_user_rule').active = False
    env.ref('portal_sale.portal_sale_order_line_rule').active = False
    env.ref('portal_sale.portal_account_invoice_user_rule').active = False
    env.ref('portal_sale.portal_account_invoice_line_rule').active = False


def uninstall_hook(cr, registry, vals=None):
    """Unarchive the overriden ir.rules"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref('portal_sale.portal_sale_order_user_rule').active = True
    env.ref('portal_sale.portal_sale_order_line_rule').active = True
    env.ref('portal_sale.portal_account_invoice_user_rule').active = True
    env.ref('portal_sale.portal_account_invoice_line_rule').active = True
