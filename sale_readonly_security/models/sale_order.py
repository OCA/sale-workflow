# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, models
from odoo.exceptions import AccessError
from odoo.tools import config


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        """Simulate that you do not have ACLs so that the create, edit and delete
        buttons are not displayed.
        """
        user = self.env.user
        group = "sale_readonly_security.group_sale_readonly_security_admin"
        test_condition = not config["test_enable"] or (
            config["test_enable"]
            and self.env.context.get("test_sale_readonly_security")
        )
        if (
            test_condition
            and operation != "read"
            and not self.env.su
            and not user.has_group(group)
        ):
            if raise_exception:
                raise AccessError(
                    _(
                        "Sorry, you are not allowed to create/edit sale orders. "
                        "Please contact your administrator for further information."
                    )
                )
            return False
        return super().check_access_rights(
            operation=operation, raise_exception=raise_exception
        )

    def _create_invoices(self, grouped=False, final=False, date=None):
        """Check if the user can do it, the method does not do a write() in sale.order,
        the computes set the corresponding values with compute methods.
        Apply the following logic: If user cannot modify a sale.order, cannot create
        an invoice.
        """
        self.env["sale.order"].check_access_rights("write")
        return super()._create_invoices(grouped=grouped, final=final, date=date)
