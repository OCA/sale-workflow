import logging

from odoo import _, http
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request

from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing
from odoo.addons.website_sale.controllers.main import PaymentPortal

_logger = logging.getLogger(__name__)


class PaymentPortal(PaymentPortal):
    @http.route(
        "/shop/payment/transaction/<int:order_id>",
        type="json",
        auth="public",
        website=True,
    )
    def shop_payment_transaction(self, order_id, access_token, **kwargs):
        try:
            self._document_check_access("sale.order", order_id, access_token)
        except MissingError as error:
            raise error
        except AccessError:
            raise ValidationError(_("The access token is invalid")) from None

        kwargs.update(
            {
                # Allow the reference to be computed based on the order
                "reference_prefix": None,
                # Include the SO to allow Subscriptions to tokenize the tx
                "sale_order_id": order_id,
            }
        )
        kwargs.pop(
            "custom_create_values", None
        )  # Don't allow passing arbitrary create values
        tx_sudo = self._create_transaction(
            custom_create_values={"sale_order_ids": [Command.set([order_id])]},
            **kwargs,
        )

        default_payment_method_id = tx_sudo.acquirer_id._get_default_payment_method_id()
        payment_method = (
            request.env["account.payment.method"]
            .sudo()
            .browse(default_payment_method_id)
        )
        so_vals = {"payment_tx_id": tx_sudo.id}
        # Set Payment Method from Acquirer
        if payment_method:
            so_vals.update({"payment_method_id": payment_method.id})

        sale_order = request.env["sale.order"].browse(order_id)
        sale_order.sudo().write(so_vals)
        sale_order.sudo().auto_set_invoice_block()

        # Store the new transaction into the transaction list and
        # if there's an old one, we remove
        # it until the day the ecommerce supports multiple orders at the same time.
        last_tx_id = request.session.get("__website_sale_last_tx_id")
        last_tx = request.env["payment.transaction"].browse(last_tx_id).sudo().exists()
        if last_tx:
            PaymentPostProcessing.remove_transactions(last_tx)
        request.session["__website_sale_last_tx_id"] = tx_sudo.id

        return tx_sudo._get_processing_values()
