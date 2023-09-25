def _add_new_columns(cr):
    cr.execute(
        """
ALTER TABLE
    sale_order
ADD COLUMN IF NOT EXISTS
    invoiced_amount numeric,
ADD COLUMN IF NOT EXISTS
    uninvoiced_amount numeric
        """
    )


def _update_amounts_for_cancel_invoices(cr):
    cr.execute(
        """
UPDATE
    sale_order
SET
    invoiced_amount = 0.0,
    uninvoiced_amount = sale_order.amount_total
WHERE
    sale_order.state = 'cancel'
    """
    )


def _update_amounts_for_non_cancel_invoices(cr):
    cr.execute(
        """
WITH amt AS(
    SELECT
        sale_order_id,
        COALESCE(SUM(amount_total_in_currency_signed), 0) AS invoiced_amount,
        CASE
            WHEN SUM(amount_total_in_currency_signed) IS NULL
                THEN amount_total
            WHEN amount_total - SUM(
                amount_total_in_currency_signed
            ) > 0.0 THEN amount_total - SUM(
                amount_total_in_currency_signed)
            ELSE 0.0
        END AS uninvoiced_amount
    FROM (
        SELECT DISTINCT
            sale_order.id AS sale_order_id,
            sale_order.amount_total AS amount_total,
            account_move.id AS account_move_id,
            account_move.amount_total_in_currency_signed as amount_total_in_currency_signed
        FROM
            sale_order
        LEFT JOIN sale_order_line
        ON sale_order_line.order_id = sale_order.id
        LEFT JOIN sale_order_line_invoice_rel
        ON sale_order_line_invoice_rel.order_line_id = sale_order_line.id
        LEFT JOIN account_move_line
        ON sale_order_line_invoice_rel.invoice_line_id = account_move_line.id
        LEFT JOIN account_move
        ON account_move_line.move_id = account_move.id
        WHERE
            sale_order.state != 'cancel'
            AND (
                account_move IS NULL
                OR (
                    account_move.move_type IN ('out_invoice', 'out_refund')
                    AND account_move.state != 'cancel'
                )
        )
    ) AS distinct_account_move
    GROUP BY sale_order_id, amount_total
)
UPDATE sale_order
    SET invoiced_amount = amt.invoiced_amount,
        uninvoiced_amount = amt.uninvoiced_amount
FROM amt
WHERE sale_order.id = amt.sale_order_id
    """
    )


def _update_amounts(cr):
    _update_amounts_for_cancel_invoices(cr)
    _update_amounts_for_non_cancel_invoices(cr)


def pre_init_hook(cr):
    """
    Add columns to avoid Memory error on an existing Odoo instance with lots of data
    """
    _add_new_columns(cr)
    _update_amounts(cr)
