from django.urls import path

from .views import OrderStepOneView, OrderStepTwoView, OrderStepThreeView, OrderStepFourView, OrderView


urlpatterns = [
    path('', OrderStepOneView.as_view(), name='order_step_1'),
    path('step2/', OrderStepTwoView.as_view(), name='order_step_2'),
    path('step3/', OrderStepThreeView.as_view(), name='order_step_3'),
    path('step4/', OrderStepFourView.as_view(), name='order_step_4'),
    path('detail/<int:order_id>/', OrderView.as_view(), name='order_detail'),
]
