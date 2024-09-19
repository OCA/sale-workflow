# Copyright 2019 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def _set_candidate_sale(env):
    """
    This post-init-hook will update last price information for all products
    """
    product_obj = env["product.template"]
    products = product_obj.search([("sale_ok", "=", True)])
    products.write({"candidate_sale": True, "sale_ok": True})
    products.write({"candidate_sale_confirm": True, "sale_ok_confirm": True})
