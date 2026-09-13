Flag orders as Forecast available according to the lines

Replicates the standard `qty_at_date_widget` logic:

**Draft/Sent orders (no moves created):**
- Issue = insufficient virtual stock AND not MTO product

**Confirmed orders (moves created):**
- Issue = insufficient stock OR late delivery (forecast_expected_date > scheduled_date)

**Confirmed sale state:**
- Uses `free_qty_today` instead of `virtual_available_at_date`

**Always ignored:**
- Lines without `scheduled_date`
- Display type lines (sections/notes)


The main goal is to filter and to warn users
