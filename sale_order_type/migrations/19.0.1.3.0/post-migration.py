def migrate(cr, version):
    cr.execute(
        "SELECT EXISTS (SELECT 1 FROM information_schema.columns "
        "WHERE table_name = 'sale_order_type' AND column_name = 'analytic_account_id')"
    )
    if not cr.fetchone()[0]:
        return
    cr.execute(
        """
        UPDATE sale_order_type
        SET analytic_distribution = jsonb_build_object(analytic_account_id::text, 100.0)
        WHERE analytic_account_id IS NOT NULL
        """
    )
