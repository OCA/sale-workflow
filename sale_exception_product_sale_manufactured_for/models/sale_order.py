# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def exception_partner_can_order_manufactured_for(self):
        """Return whether the partner can order all the items in the sale

        Used in a sales exception. Returns true only if the partner set in
        the sales order can buy all the products. This will happen if:
        1. it has a commercial entity that is listed as one of the
           partners for which the products can be manufactured for.
        2. it doesn't have a commercial entity and none of the products
           on the sale order have any restriction.
        """
        self.ensure_one()
        commercial_entity = self.partner_id.commercial_partner_id

        self.env.cr.execute(
            """
            SELECT rel.product_id, ARRAY_AGG(rel.partner_id)
            FROM sale_order_line sol
                JOIN product_product prod ON (sol.product_id = prod.id)
                JOIN product_product_manuf_for_partner_rel rel ON (rel.product_id = prod.id)
            WHERE sol.display_type IS NULL
                AND sol.order_id = %s
            GROUP BY rel.product_id
        """,
            (self.id,),
        )
        for _, allowed_partner_ids in self.env.cr.fetchall():
            # The product has limitations but the partner doesn't have
            # a commercial entity, thus the condition is not fulfilled.
            if not commercial_entity and allowed_partner_ids:
                return False

            # The product has limitations and the commercial entity of
            # the partner partner is not listed as allowed.
            elif commercial_entity.id not in allowed_partner_ids:
                return False

        return True
