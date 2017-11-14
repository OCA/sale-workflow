# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from odoo.addons.sale.models.sale import SaleOrder


def post_load_hook():

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
        precision = self.env['decimal.precision'].\
            precision_get('Product Unit of Measure')

        # START HOOK
        # As now from the beginning there can be invoices related to that
        # order, instead of new invoices, new lines are taking into account in
        # order to know whether there are invoice lines or not
        new_lines = False
        # END HOOK
        for order in self:
            # START HOOK
            # Add more flexibility in grouping key fields
            # WAS: group_key = order.id if grouped
            # else (order.partner_invoice_id.id, order.currency_id.id)
            group_key = order.id if grouped else \
                self._get_invoice_group_key(order)
            # 'invoice' must be always instantiated respecting the old logic
            if group_key in invoices:
                invoice = invoices[group_key]
            # END HOOK
            for line in order.order_line.sorted(
                    key=lambda l: l.qty_to_invoice < 0):
                if float_is_zero(line.qty_to_invoice,
                                 precision_digits=precision):
                    continue
                if group_key not in invoices:
                    inv_data = order._prepare_invoice()
                    invoice = inv_obj.create(inv_data)
                    references[invoice] = order
                    invoices[group_key] = invoice
                elif group_key in invoices:
                    # START HOOK
                    # This line below is added in order to cover cases where an
                    # invoice is not created and instead a draft one is picked
                    invoice = invoices[group_key]
                    # END HOOK
                    vals = {}
                    if order.name not in invoices[group_key].\
                            origin.split(', '):
                        vals['origin'] = invoices[group_key].origin + ', ' + \
                            order.name
                    if order.client_order_ref and order.client_order_ref not \
                            in invoices[group_key].name.split(', ') and \
                            order.client_order_ref != invoices[group_key].name:
                        vals['name'] = invoices[group_key].name + ', ' +\
                            order.client_order_ref
                    invoices[group_key].write(vals)
                if line.qty_to_invoice > 0:
                    line.invoice_line_create(invoices[group_key].id,
                                             line.qty_to_invoice)
                    # START HOOK
                    # Change to true if new lines are added
                    new_lines = True
                    # END HOOK
                elif line.qty_to_invoice < 0 and final:
                    line.invoice_line_create(invoices[group_key].id,
                                             line.qty_to_invoice)
                    # START HOOK
                    # Change to true if new lines are added
                    new_lines = True
                    # END HOOOK

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoice] = references[invoice] | order

        # START HOOK
        # WAS: if not invoices:
        # Check if new lines have been added in order to determine whether
        # there are invoice lines or not
        if not new_lines:
            raise UserError(_('There is no invoicable line.'))
        # END HOOK

        for invoice in invoices.values():
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
            invoice.message_post_with_view(
                'mail.message_origin_link',
                values={'self': invoice, 'origin': references[invoice]},
                subtype_id=self.env.ref('mail.mt_note').id)
        return [inv.id for inv in invoices.values()]

    if not hasattr(SaleOrder, 'action_invoice_create_original'):
        SaleOrder.action_invoice_create_original = \
            SaleOrder.action_invoice_create

    SaleOrder.action_invoice_create = new_action_invoice_create
