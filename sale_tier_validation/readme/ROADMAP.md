- The sales order, when moved to the state sent, will still send the
  email even if the validation is not approved by the corresponding
  tier. Code to consider this particular case is not developed.
- If any module modifies the attrs of the confirm sales order button,
  it will invalidate the expected behavior.