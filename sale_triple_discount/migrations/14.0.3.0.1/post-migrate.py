from openupgradelib import openupgrade

# pylint: disable=W7950
from odoo.addons.sale_triple_discount.hooks import post_init_hook


@openupgrade.migrate()
def migrate(env, version):
    post_init_hook(env.cr, env)
