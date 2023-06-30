{{ cookiecutter.__repo }}
{% for _ in cookiecutter.__repo -%}={%- endfor %}

{{ cookiecutter.short_description }}

.. toctree::
   :hidden:

   self

.. social-card:: {% if cookiecutter.add_layout == 'True' %}{ "cards_layout": "cool_new_layout" }{% endif %}
   :dry-run:

   {% if cookiecutter.add_layout != 'True' and (cookiecutter.add_context == 'True' or cookiecutter.add_image == 'True') -%}
   layers:
     - background: {}
     {%- if cookiecutter.add_context == 'True' %}
     - typography:
         content: "{{ '{{' }} plugin.{{ cookiecutter.package_name }}.example }}"
         line: { amount: 2 }
     {%- endif %}
     {%- if cookiecutter.add_image == 'True' %}
     - icon: { image: cool_new_image.png }
       size: { x: 940, y: 215 }
       offset: { width: 200, height: 200 }
       rectangle: { border: 5, color: black }
     {%- endif -%}
   {%- endif %}
