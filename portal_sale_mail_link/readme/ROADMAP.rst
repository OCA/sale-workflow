* The button template is hardcoded, so styling will be quite limited (we should
  monkeypatch the method and translations in a custom module). Maybe an optional
  solution could be making a generic mako injector, with an extra html field in
  the template that we'd inject if set and an extra module for sale with the
  data already prepared for the sale template.
