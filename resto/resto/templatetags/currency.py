from django import template

register = template.Library()

@register.filter
def rupiah(value):
    try:
        val = float(value)
    except (TypeError, ValueError):
        return value
    return f"Rp {val:,.0f}".replace(",", ".")
