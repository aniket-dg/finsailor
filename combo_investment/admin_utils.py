import json
from django import forms
from django.utils.html import mark_safe


class JSONEditor(forms.Textarea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs["class"] = "json-editor"
        self._cm_json_options = json.dumps(
            {
                "lineNumbers": True,
                "mode": {"name": "javascript", "json": True},
                "lineWrapping": True,
                "matchBrackets": True,
            }
        )

    def render(self, name, value, attrs=None, renderer=None):
        """Serves the JS code to initialise the CodeMirror text area."""
        # Sort-of a hack to get JSON auto-formatting
        value_fmt = json.dumps(json.loads(value), indent=2)
        output_lines = [
            super().render(name, value_fmt, attrs, renderer),
            '<script type="text/javascript">',
            f'el=document.getElementById("id_{name}")',
            f"cm=CodeMirror.fromTextArea(el, {self._cm_json_options});",
            'cm.setSize("80ch", "120ch");',  # 80 characters wide, and 50% longer.
            # "el.nextElementSibling.style.height='auto';",
            "</script>",
        ]
        return mark_safe("\n".join(output_lines))

    class Media:
        css = {
            "all": (
                "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.59.1/codemirror.min.css",
            )
        }

        js = (
            "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.59.1/codemirror.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.59.1/addon/edit/matchbrackets.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.59.1/mode/javascript/javascript.min.js",
        )
