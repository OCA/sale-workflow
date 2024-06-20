This module adds the concept of promotion rules that can be applied on
the sale order.

Two kinds of rules are implemented:  
- automatic
- coupon

Automatic rules are applied/recomputed automatically for a sale order
when the user clicks on the button "Apply discount" in the view form.
Depending on the rule's criteria more than one automatic rule can be
applied to a same sale order.

Coupon are special manual rules. Only one coupon can be applied to a
sale order. This rule takes always precedence over automatic rules.

![Promotion rules screenshot](../sale_promotion_rule/static/description/promotion_rule.png)
