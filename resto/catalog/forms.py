from django import forms
from .models import Category, MenuItem

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "code"]

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ["category", "name", "description", "price", "stock_qty", "is_active", "image"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3})
        }

    def clean_price(self):
        v = self.cleaned_data["price"]
        if v < 0:
            raise forms.ValidationError("Harga tidak boleh negatif.")
        return v

    def clean_stock_qty(self):
        v = self.cleaned_data["stock_qty"]
        if v < 0:
            raise forms.ValidationError("Stok tidak boleh negatif.")
        return v
