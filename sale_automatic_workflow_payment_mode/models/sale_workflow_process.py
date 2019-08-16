# © 2016 Camptocamp SA, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class SaleWorkflowProcess(models.Model):
    _inherit = "sale.workflow.process"

    @api.model
    def _default_payment_filter_id(self):
        xmlid = ('sale_automatic_workflow_payment_mode.'
                 'automatic_workflow_payment_filter')
        try:
            return self.env.ref(xmlid)
        except ValueError:
            return self.env['ir.filters'].browse()

    payment_filter_id = fields.Many2one(
        'ir.filters',
        string='Register Payment Invoice Filter',
        default=_default_payment_filter_id,
    )
    register_payment = fields.Boolean(string='Register Payment')
    payment_filter_domain = fields.Text(
        string='Payment Filter Domain',
        related='payment_filter_id.domain',
    )
