- Only quotations in state *Quotation* and *Quotation Sent* can be merged.
  Merging confirmed orders would require moving the related deliveries and
  invoices, which is out of the scope of this module.
- Merged lines keep the price of their original quotation; the pricelist of the
  merged quotation is not re-applied.
- Sections are not deduplicated: two quotations carrying the same section end up
  as two sections. A line consolidated into an existing one also leaves its own
  section behind, which may stay empty.
