# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AutomaticWorkflowJob(models.Model):

    _inherit = "automatic.workflow.job"

    def _do_create_invoice(self, sale, domain_filter):
        """
        To avoid to override many functions,
        just override this function to update invoices after creating them.
        """
        current_invoices = sale.invoice_ids
        res = super()._do_create_invoice(sale, domain_filter)
        created_invoices = sale.invoice_ids - current_invoices
        if created_invoices:
            default_values = sale.workflow_process_id.create_invoice_default_value_ids

            values = {}
            for default_value in default_values:
                if default_value.value_type == "default_char_value":
                    value = default_value.default_char_value
                else:  # value_type == "from_sale_order"
                    value = getattr(sale, default_value.sale_order_field_id.name)
                if value:
                    values[default_value.invoice_field_id.name] = value
            if values:
                created_invoices.write(values)
        return res
