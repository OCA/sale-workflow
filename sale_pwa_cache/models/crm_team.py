# Copyright 2021 Tecnactiva - Alexandre Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "crm.team"

    def _compute_dashboard_graph(self):
        """ Avoid UserError exceptions to complete
        prefetch task. This is caused because Odoo
        defines some data only for 'iap'.
        """
        try:
            super()._compute_dashboard_graph()
        except UserError:
            self.dashboard_graph_data = ""
