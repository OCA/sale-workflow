def post_init_hook(env):
    lines = env["sale.order.line"].search(
        [("display_type", "=", False), ("product_id", "!=", False)]
    )
    hidden_lines = env["sale.order.line"]
    for line in lines:
        product_name = line.with_context(
            lang=line.order_id._get_lang()
        )._get_product_display_name()
        if line.name and product_name and product_name not in line.name:
            hidden_lines |= line
    if hidden_lines:
        env.cr.execute(
            """
                UPDATE sale_order_line
                SET hide_product_name = TRUE
                WHERE id = ANY(%s)
            """,
            (hidden_lines.ids,),
        )
