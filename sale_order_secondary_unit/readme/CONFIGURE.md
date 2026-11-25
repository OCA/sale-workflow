To configure this module, you need to:

1.  Go to *Sales \> Configuration \> Products \> Secondary Units of
    Measure* to manage all the 'Secondary Units of Measure' in the
    system.

For configuration details on displaying secondary unit information in the sale report and portal,
please refer to the product_secondary_unit configuration guide.

## Settings Visibility

When installing this module, all internal users are automatically added to the
`product_secondary_unit.group_sale_secondary_unit` security group. This makes
the Sales-related "Hide Secondary Qty Column" and "Secondary Unit Price Display"
settings visible in **Settings > Units of Measure**.

If you installed this module before these report presentation settings were introduced
in `product_secondary_unit`, users may not see these configuration options. To fix this:

1. Go to **Settings > Users & Companies > Groups**
2. Search for "Sale Secondary Unit"
3. Add the relevant users to that group
