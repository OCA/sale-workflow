# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import SUPERUSER_ID, api


def set_default_partner_product_filter(cr, registry):
    """This hook is here because we couldn't set the default filter
    as a default value for partners.

    When the module is installed, Odoo creates the new field and at the
    same time tries to set the default value for all existing records in
    the DB. However the XML data (and thus 'product_filter_default' filter)
    is still not created at this stage.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    partners_to_update = (
        env["res.partner"]
        .with_context(active_test=False)
        .search([("pricelist_cache_product_filter_id", "=", False)])
    )
    default_filter = env.ref("pricelist_cache.product_filter_default")
    partners_to_update.write({"pricelist_cache_product_filter_id": default_filter.id})
