# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from contextlib import contextmanager

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    customer_ref = fields.Char(related="move_id.customer_ref", readonly=True)

    def write(self, vals):
        # Overridden to update related result packages
        with self.update_related_packages(vals):
            res = super().write(vals)
        return res

    @contextmanager
    def update_related_packages(self, vals):
        """Keep packages in sync."""
        # FIXME: is not granted that all the lines involved by the pkg will be updated here.
        # We should look for all lines linked to the same picking and update them all.
        result_package_updated = "result_package_id" in vals
        if result_package_updated:
            old_packages = self.result_package_id
        yield
        if result_package_updated:
            self._update_related_packages(old_packages)

    def _update_related_packages(self, old_packages):
        # Remove Customer Ref. from packages that are used anymore
        new_package = self.result_package_id
        (old_packages - new_package).write(self._update_related_old_pkg_vals())
        # Collect all Customer Ref. from lines and store them in the package
        new_package.write(self._update_related_new_pkg_vals())

    def _update_related_old_pkg_vals(self):
        return {"customer_ref": False}

    def _update_related_new_pkg_vals(self):
        return {
            "customer_ref": ", ".join(
                sorted({x.customer_ref for x in self if x.customer_ref})
            )
        }
