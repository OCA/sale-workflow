#  Copyright 2019 Tecnativa - Sergio Teruel
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    # Remove old security group_uom from product template view because now has
    # a new group for secondary units
    group_uom = env.ref('product.group_uom')
    view_product_template = env.ref(
        'sale_order_secondary_unit.product_template_form_view')
    view_product_template.write({
        'groups_id': [(3, group_uom.id)]
    })

    # Remove old security group_uom from sale order view because now has a
    # new group for secondary units
    view_product_template = env.ref(
        'sale_order_secondary_unit.view_order_form')
    view_product_template.write({
        'groups_id': [(3, group_uom.id)]
    })
