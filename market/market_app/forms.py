from django import forms


class ProductReviewForm(forms.Form):
    description = forms.CharField(max_length=2000)
    # Эту часть ввести после добавления загрузки фото с отзывами
    # images = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
