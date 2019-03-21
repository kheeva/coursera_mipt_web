from django import forms


class ItemForm(forms.Form):
    title = forms.CharField(min_length=1, max_length=64)
    description = forms.CharField(min_length=1, max_length=1024)
    price = forms.IntegerField(min_value=1, max_value=1000000)


class ReviewForm(forms.Form):
    grade = forms.IntegerField(min_value=1, max_value=10)
    text = forms.CharField(min_length=1, max_length=1024)
