# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PaymentTransaction(models.Model):

    _inherit = "payment.transaction"

    def _update_sale_order_workflow(self):
        """
        Update the Sale Order with payment acquirer workflow
        """
        for transaction in self.filtered(lambda t: t.acquirer_id.workflow_process_id):
            transaction.sale_order_ids.write(
                {"workflow_process_id": transaction.acquirer_id.workflow_process_id}
            )

    @api.model_create_multi
    def create(self, vals_list):
        transactions = super().create(vals_list)
        transactions._update_sale_order_workflow()
        return transactions
