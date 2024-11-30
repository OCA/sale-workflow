# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, exceptions, models


class ProductPackagingLevel(models.Model):
    _inherit = "product.packaging.level"

    @api.constrains("can_be_sold")
    def _check_sell_only_by_packaging_can_be_sold_packaging_ids(self):
        for record in self:
            if record.can_be_sold:
                continue
            products = record.packaging_ids.product_id
            templates = products.product_tmpl_id
            try:
                templates._check_sell_only_by_packaging_can_be_sold_packaging_ids()
            except exceptions.ValidationError as e:
                raise exceptions.ValidationError(
                    self.env._(
                        'Packaging level %s must stay with "Can be sold",'
                        ' at least one product configured as "sell only'
                        ' by packaging" is using it.',
                        record.display_name,
                    ),
                ) from e
