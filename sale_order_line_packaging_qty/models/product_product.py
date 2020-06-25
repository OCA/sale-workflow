# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _which_pack_multiple(self, qty):
        """ Return multiple of product packaging for one quantity if exist.
        """
        self.ensure_one()
        pack_multiple = False
        if qty:
            for pack in self.packaging_ids.sorted("qty", reverse=True):
                if pack.packaging_type_id.can_be_sold and pack.qty:
                    if (qty % pack.qty) == 0:
                        pack_multiple = pack
                        break
        return pack_multiple
