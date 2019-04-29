# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_invoice_group_key(self, order):
        return (order.partner_invoice_id.id, order.currency_id.id)

    @api.model
    def _get_invoice_group_line_key(self, line):
        return self._get_invoice_group_key(line.order_id)

    @api.model
    def _get_draft_invoices(self, invoices, references):
        return invoices, references

    @api.model_cr
    def _register_hook(self):

        def new_action_invoice_create(self, grouped=False, final=False):
            """
            Create the invoice associated to the SO.
            :param grouped: if True, invoices are grouped by SO id. If False,
            invoices are grouped by (partner_invoice_id, currency)
            :param final: if True, refunds will be generated if necessary
            :returns: list of created invoices
            """
            if not hasattr(self, '_get_invoice_group_key'):
                return self.action_invoice_create_original(grouped=grouped,
                                                           final=final)
            invoices = {}
            references = {}

            # START HOOK
            # Take into account draft invoices when creating new ones
            self._get_draft_invoices(invoices, references)
            # END HOOK

            inv_obj = self.env['account.invoice']
            precision = self.env['decimal.precision']. \
                precision_get('Product Unit of Measure')

            # START HOOK
            # As now from the beginning there can be invoices related to that
            # order, instead of new invoices,
            # new lines are taking into account in
            # order to know whether there are invoice lines or not
            new_lines = False
            # END HOOK
            for order in self:
                # We only want to create sections that
                # have at least one invoiceable line
                pending_section = None
                for line in order.order_line.sorted(
                        key=lambda l: l.qty_to_invoice < 0):
                    if line.display_type == 'line_section':
                        pending_section = line
                        continue
                    if float_is_zero(line.qty_to_invoice,
                                     precision_digits=precision):
                        continue
                    # START HOOK
                    # Allow to check if a line should not be invoiced
                    if line._do_not_invoice():
                        continue
                    # END HOOK
                    # START HOOK
                    # Add more flexibility in grouping key fields
                    # WAS: group_key = order.id if grouped
                    # else (order.partner_invoice_id.id, order.currency_id.id)
                    group_key = order.id if grouped else \
                        self._get_invoice_group_line_key(line)
                    # 'invoice' must be always instantiated
                    # respecting the old logic
                    if group_key in invoices:
                        invoice = invoices[group_key]
                        # END HOOK
                    if group_key not in invoices:
                        inv_data = line._prepare_invoice()
                        invoice = inv_obj.create(inv_data)
                        references[invoice] = order
                        invoices[group_key] = invoice
                    elif group_key in invoices:
                        # START HOOK
                        # This line below is added in order
                        # to cover cases where an invoice is not created
                        # and instead a draft one is picked
                        invoice = invoices[group_key]
                        # END HOOK
                        vals = {}
                        if order.name not in invoice. \
                                origin.split(', '):
                            vals['origin'] = \
                                invoice.origin + ', ' + order.name
                        if order.client_order_ref and order.client_order_ref \
                                not in invoice.name.split(', ') \
                                and order.client_order_ref != invoice.name:
                            vals['name'] = \
                                invoice.name + ', ' + \
                                order.client_order_ref
                        invoice.write(vals)
                    if line.qty_to_invoice > 0 or \
                            (line.qty_to_invoice < 0 and final):
                        if pending_section:
                            pending_section.invoice_line_create(
                                invoices[group_key].id,
                                pending_section.qty_to_invoice
                            )
                            pending_section = None
                        line.invoice_line_create(invoices[group_key].id,
                                                 line.qty_to_invoice)
                        # START HOOK
                        # Change to true if new lines are added
                        new_lines = True
                        # END HOOK
                    if references.get(invoices.get(group_key)):
                        if order not in references[invoices[group_key]]:
                            references[invoice] = references[invoice] | order

            # START HOOK
            # WAS: if not invoices:
            # Check if new lines have been added in order to determine whether
            # there are invoice lines or not
            if not new_lines and \
                    not self.env.context.get('no_check_lines', False):
                raise UserError(_('There is no invoicable line.'))
            # END HOOK

            for invoice in invoices.values():
                invoice.compute_taxes()
                if not invoice.invoice_line_ids:
                    raise UserError(_('There is no invoicable line.'))
                # If invoice is negative, do a refund invoice instead
                if invoice.amount_untaxed < 0:
                    invoice.type = 'out_refund'
                    for line in invoice.invoice_line_ids:
                        line.quantity = -line.quantity
                # Use additional field helper function (for account extensions)
                for line in invoice.invoice_line_ids:
                    line._set_additional_fields(invoice)
                # Necessary to force computation of taxes. In account_invoice,
                # they are triggered by onchanges, which are not triggered when
                # doing a create.
                invoice.compute_taxes()
                # Idem for partner
                so_payment_term_id = invoice.payment_term_id.id
                invoice._onchange_partner_id()
                # To keep the payment terms set on the SO
                invoice.payment_term_id = so_payment_term_id
                invoice.message_post_with_view(
                    'mail.message_origin_link',
                    values={'self': invoice, 'origin': references[invoice]},
                    subtype_id=self.env.ref('mail.mt_note').id)
            return [inv.id for inv in invoices.values()]

        self._patch_method('action_invoice_create', new_action_invoice_create)

        return super(SaleOrder, self)._register_hook()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice(self):
        return self.order_id._prepare_invoice()

    def _do_not_invoice(self):
        return False
