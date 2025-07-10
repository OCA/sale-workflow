# Copyright (C) 2024 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

# pylint: disable=W8150
from odoo.addons.sale_order_ordered_weight import pre_init_hook


@openupgrade.migrate()
def migrate(env, version):
    # we recompute the weights because in previous implementation,
    # 1) the UoM conversion was not done, so the value could be incorrect
    # 2) the recompute was not done when the weight of the product has changed
    # so the value could be obsolete.
    pre_init_hook(env.cr)
