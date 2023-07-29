Preset Gradients
================

A generated list of the available gradient presets. Each section of this page contains the
string value of the preset and the alternative integer (in parentheses) corresponding to the named
preset.

.. seealso::

   - `linear_gradient.preset <Linear_Gradient.preset>`
   - `radial_gradient.preset <Radial_Gradient.preset>`
   - `conical_gradient.preset <Conical_Gradient.preset>`

.. jinja:: gradient_presets

    {% for index, name in presets.items() %}
    {{ name }} ({{ index }})
    {% for _ in name %}{{ '-' }}{% endfor %}------

    {% for grad in ['radial', 'linear', 'conical'] %}
    .. image-generator::
        :width: 30%

        size: { width: 250, height: 250 }
        layers:
          - {% if grad == 'linear' %}background{% else %}ellipse{% endif %}:
              {{grad}}_gradient:
                preset: {{ name }}
                # or equivalently
                # preset: {{ index }}
                {% if grad == 'linear' -%}
                start: { y: 125 }
                end: { x: 250, y: 125 }
                {%- else -%}
                center: { x: 125, y: 125 }
                {% if grad == 'radial' -%}
                radius: 125
                {%- else %}
                angle: 0
                {%- endif %}
                {%- endif %}
    {% endfor %}
    {% endfor %}
