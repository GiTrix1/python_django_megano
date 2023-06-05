from django.urls import path
from .views import AccountView, ProfileView, ProfileSuccessView, HistoryOrderView, HistoryViewView

urlpatterns = [
    path('', AccountView.as_view(), name='account'),
    path('edit/', ProfileView.as_view(), name='profile'),
    path('edit/success/', ProfileSuccessView.as_view(), name='profilesuccess'),
    path('history_order/', HistoryOrderView.as_view(), name='historyorder'),
    path('history_view/', HistoryViewView.as_view(), name='historyview'),
]
