# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def post_init_hook(env):
    """Archive the core access records we want to override"""
    env.ref("sale.sale_order_rule_portal").active = False


def uninstall_hook(env):
    """Unarchive the overridden core access records"""
    env.ref("sale.sale_order_rule_portal").active = True
