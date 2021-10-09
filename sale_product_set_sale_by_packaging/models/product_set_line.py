# Copyright 2021 Camptocamp SA
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging
from collections import defaultdict

from odoo import _, api, exceptions, fields, models
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class ProductSetLine(models.Model):
    _inherit = "product.set.line"

    # Just for UI purpose
    sell_only_by_packaging = fields.Boolean(related="product_id.sell_only_by_packaging")

    # The warning is because field "sell_only_by_packaging" is related,
    # non-store, non-inherit so not writeable
    @api.constrains("sell_only_by_packaging", "product_packaging_id")
    def _check_sell_only_by_packaging(self):
        errored = self.filtered(
            lambda x: x.product_id.sell_only_by_packaging and not x.product_packaging_id
        )
        if errored:
            raise exceptions.UserError(
                self._check_sell_only_by_packaging_err_msg(errored)
            )

    def _check_sell_only_by_packaging_err_msg(self, lines):
        return _(
            "The following product(s) can be sold only by packaging: \n   %s"
        ) % ", ".join(lines.mapped("product_id.display_name"))

    @api.model
    def cron_check_packaging(self):
        """Ensure lines are tied to the right packaging.

        When

        * packaging cannot be sold anymore
        * lines are tied to a product that can be sold only by packaging
          and have no packaging

        change the packaging on the line to the 1st saleable packaging.
        """

        # Pick lines with packaging that cannot be sold
        # or have no packaging
        line_domain = expression.OR(
            [
                [("product_packaging_id.can_be_sold", "=", False)],
                [
                    ("product_packaging_id", "=", False),
                    ("product_id.sell_only_by_packaging", "=", True),
                ],
            ]
        )
        self._fix_lines_packaging(line_domain)

    def _fix_lines_packaging(self, line_domain):
        lines = self.search(line_domain, order="product_id")
        lines_by_product = defaultdict(self.browse)
        for line in lines:
            lines_by_product[line.product_id] += line

        # Change packaging to the 1st available for the product
        for product, lines in lines_by_product.items():
            first_valid_pkg = self._get_product_first_valid_packaging(product)
            if not first_valid_pkg:
                _logger.error(
                    "Cannot find a valid packaging for product ID %s", product.id
                )
                continue
            lines.write(
                {"product_packaging_id": first_valid_pkg.id, "product_packaging_qty": 1}
            )
            _logger.info("Fixed packaging on set lines for product ID %s", product.id)

    def _get_product_first_valid_packaging(self, product):
        return fields.first(
            product.packaging_ids.filtered(lambda x: x.can_be_sold).sorted("qty")
        )
