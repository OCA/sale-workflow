def post_init_hook(cr, registry):
    """Filling new columns"""
    cr.execute(
        """
        UPDATE product_template
        SET sale_delay_range_value = sale_delay
        """
    )

    cr.execute(
        """
        UPDATE sale_order_line
        SET customer_lead_range_value = customer_lead
        """
    )
