def pre_init_hook(cr):
    # Add new column to avoid computing at install
    cr.execute(
        "ALTER TABLE sale_order "
        "ADD COLUMN IF NOT EXISTS stock_is_reserved BOOLEAN default(FALSE)"
    )
    cr.execute("ALTER TABLE sale_order alter column stock_is_reserved drop default")
