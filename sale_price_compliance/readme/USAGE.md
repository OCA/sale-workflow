To use this module, you need to:

**Configure Parameter Text: Change the default price compliance tiers texts**
1. Go to System Parameters.
1. Create a new parameter with key `sale_price_compliance.price_compliance_selection_tiers_text`.
1. Write a *dictionary* with the values for tiers that you want to change it's default text.
1. Save the parameter.
1. Create a new parameter with key `sale_price_compliance.price_compliance_selection_tiers_icon`.
1. Write a *dictionary* with the values for tiers that you want to change it's default icon.
1. Save the parameter.

Example:

Param *sale_price_compliance.price_compliance_selection_tiers_text*:

{'t1': 'Gold', 't2': 'Silver', 't3': 'Bronze', 'pricelist': 'Draw'}

Param *sale_price_compliance.price_compliance_selection_tiers_icon*:

{'t1': '🥇', 't2': '🥈', 't3': '🥉', 'non_compliant': '⛔️', 'pricelist': '🤝'}

Resulting texts and icons will be:

- Gold: 🥇
- Silver: 🥈
- Bronze: 🥉
- Non Compliant: ⛔️
- Draw: 🤝

Available keys to be used in the dictionary are:

- t1: Tier 1
- t2: Tier 2
- t3: Tier 3
- non_compliant: Non Compliant
- pricelist: Pricelist

**Configure: Product Price Compliance Thresholds configuration**
1. Go to Sales > Products > Products > Select one > Sales tab
1. Enable Use Price Compliance Thresholds under Sale Price Compliance Thresholds
1. Fill from 1 to 3 tiers that you want to use in this product.

Example:
Tier 1: 10%, Tier 2: 20%, Tier 3: 30%. (Use all tiers)

**Configure: Product Category Price Compliance Thresholds configuration**
1. Go to Sales > Configuration > Products > Product Categories > Select one
1. Enable Use Price Compliance Thresholds under Sale Price Compliance Thresholds
1. Fill from 1 to 3 tiers that you want to use in this category.

Example:
Tier 1: 15%, Tier 2: 25%, Tier 3: 0%. (Don't use tier 3)

**Configure: Company Price Compliance Thresholds configuration**
1. Go to Sales > Configuration > Settings
1. Enable Use Price Compliance Thresholds under Pricing section
1. Fill from 1 to 3 tiers that you want to use for the company.

Example:
Tier 1: 30%, Tier 2: 0%, Tier 3: 0%. (Don't use tier 2 and 3)


**Sale: As a Salesman user**
1. Create a new sale and fill contact field
1. Add a new line with a product that has been configured to use Price Compliance
1. Click on the 🟩, 🟨, 🟧, 🟥 or 🟦 icon at the start of the line.
1. You will see a popup with useful information about the Tier ranges.
1. Play with it and then set a Non Compliant price (change price or discount to achieve this).
1. Try to confirm the Sale and see the error.

**Sale: As a Sales Administrator**
1. Confirm the previous Sale.
1. See the message on the chatter.


**Reporting: Sales report**
1. Go to Sales > Reporting > Sales
1. Select bar chart or Pivot view
1. Group by Price Compliance Level

**Reporting: Salesperson report**
1. Go to Sales > Reporting > Salesperson
1. Select Bar chart + stacked or Pivot view
1. Group by Price Compliance Level

**Reporting: Product report**
1. Go to Sales > Reporting > Product
1. Select Pie chart + stacked or Pivot view
1. Group by Price Compliance Level

**Reporting: Customers report**
1. Go to Sales > Reporting > Customers
1. Select Bar chart + stacked or Pivot view
1. Group by Price Compliance Level
