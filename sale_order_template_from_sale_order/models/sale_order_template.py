# Copyright 2026 Cetmix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.exceptions import AccessError


class SaleOrderTemplate(models.Model):
    _inherit = "sale.order.template"

    def _check_salesman_can_modify(self):
        """Raise when a salesman changes a template created by someone else.

        Sales managers are not limited. ``group_sale_manager`` implies
        ``group_sale_salesman``, so this check must not treat every salesman
        group member the same way.

        :raise AccessError: the user is a salesman and did not create one of
            the templates in ``self``
        :return: None
        :rtype: None
        """
        if self.env.su or self.env.user.has_group("sales_team.group_sale_manager"):
            return
        if self.filtered(lambda template: template.create_uid != self.env.user):
            raise AccessError(
                self.env._("You can only modify quotation templates you created.")
            )
