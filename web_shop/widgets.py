from django.forms import widgets
from django.utils.encoding import force_text
from django.utils.html import conditional_escape, format_html
from itertools import chain
from models.attributes import Attribute, AttributeValue

class MultiAttributeValueSelect(widgets.SelectMultiple):
    
      def render_options(self, choices, selected_choices):
        # Normalize to strings.
        #import pdb
        #pdb.set_trace()

        selected_choices = set(force_text(v) for v in selected_choices)
        output = []
        for option_value, option_label in chain(self.choices, choices):
            if isinstance(option_label, (list, tuple)):
                output.append(format_html('<optgroup label="{0}">', force_text(option_value)))
                for option in option_label:
                    output.append(self.render_option(selected_choices, *option))
                output.append('</optgroup>')
            else:
                output.append(self.render_option(selected_choices, option_value, option_label))
        return '\n'.join(output)
