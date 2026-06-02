Layer Mask attribute
~~~~~~~~~~~~~~~~~~~~

.. py:class:: Mask

    If specified, this attribute will define a bump mask. This value can only be 1
    `layer <Mask>` with an optional `invert` attribute. Any transparent part of the
    `mask <Mask>` layer will be removed from the current `layer <Layer>` for which the
    `mask <Mask>` is defined.

    This attribute that can be used as a cropping mechanism.

    .. important::
        :title: Meaning of a mask layer's Size and Offset

        Where "current layer" is the layer in which the `mask <Layer.mask>` attribute is
        set:

        - The mask layer's `offset <Offset>` is relative the current layer's `offset
          <Offset>`.
        - The resulting mask layer's `size <Size>` (after rendering) is expanded or
          cropped to the current layer's `size <Size>`.

    .. md-tab-set::

        .. md-tab-item:: Text as a mask

            .. social-card::
                :dry-run:

                layers:
                  - background: { color: "#4051B2" }
                  - background: { image: images/rainbow.png }
                    mask:
                      typography:
                        content: This string was used as a mask.
                        line:
                          height: 1.2
                          amount: 3
                        align: center

        .. md-tab-item:: Text as a layer

            .. social-card::
                :dry-run:

                layers:
                  - background: { color: "#4051B2" }
                  - typography:
                      content: This string was used as a mask.
                      color: '{{ layout.color | yaml }}'
                      line:
                        height: 1.2
                        amount: 3
                      align: center

        .. md-tab-item:: Rectangle as a mask

            .. social-card::
                :dry-run:

                layers:
                  - background: { color: "#4051B2" }
                  - background: { image: images/rainbow.png }
                    mask:
                      size: { width: 600, height: 315 }
                      offset: { x: 300, y: 158 }
                      rectangle:
                        color: '#FFFFFF3F' # a transparent color
                        radius: 100
                        border:
                          width: 50
                          color: white

        .. md-tab-item:: Rectangle as a layer

            .. social-card::
                :dry-run:

                layers:
                  - background: { color: '#4051B2' }
                  - size: { width: 600, height: 315 }
                    offset: { x: 300, y: 158 }
                    rectangle:
                      color: '#FFFFFF3F' # a transparent color
                      radius: 100
                      border:
                        width: 50
                        color: white

    .. py:attribute:: invert
        :type: bool
        :value: False

        Use this `bool` attribute to cause the mask layer's transparency to become
        inverted. This is only useful if excluding pixels from the layer's image is desired.

        .. jinja::

            .. md-tab-set::

                .. md-tab-item:: Excluding an image

                    .. social-card::
                        :dry-run:

                        layers:
                          - background: { color: '#4051B2' }
                          # this red background is drawn to prove the transparency of the mask
                          - background: { color: red }
                            offset: { x: 600, y: 0 }
                          - size: { width: 200, height: 200 }
                            offset: { x: 500, y: 215 }
                            rectangle:
                              color: green
                              radius: 50
                            mask:
                              invert: true
                              size: { width: 150, height: 150 }
                              offset: { x: 25, y: 25 }
                              icon: { image: 'simple/sphinx' }

                {% for offset in ['negative', 'same', 'positive'] %}
                .. md-tab-item:: Excluding with {{ offset }} offset

                    .. social-card::
                        :dry-run:

                        layers:
                          - background: { color: '#4051B2' }
                          - background: { color: white }
                            offset: { x: 450, y: 150 }
                            size: { width: 300, height: 300 }
                            mask:
                              invert: true
                              size: { width: 300, height: 300 }
                              {% if offset != 'same' -%}
                              offset: { x: {% if offset == 'negative' %}-{% endif %}150, y: 0 }
                              {%- endif %}
                              ellipse: { color: '#0000003f' }
                {% endfor %}
