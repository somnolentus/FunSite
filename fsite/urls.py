from django.urls import path
from .views import AdvertismentList, register, endreg, UserUpdateView, UserView, AdvertismentCreate, AdvertismentUpdate, \
    AdvertismentDetail, CommentCreate, comment_accept, comment_delete, subscribe


urlpatterns = [
    path('', AdvertismentList.as_view(), name='advertisments'),
    path('register/', register, name="register"),
    path('activation_code_form/', endreg, name="endreg"),
    path('<int:pk>/', AdvertismentDetail.as_view(), name='advertisment'),
    path('add/', AdvertismentCreate.as_view(), name='advertisment_create'),
    path('<int:pk>/edit/', AdvertismentUpdate.as_view(), name='advertisment_update'),
    path('<int:pk>/comment/', CommentCreate.as_view(), name='comment_create'),
    path('<int:pk>/accept/', comment_accept, name='comment_accept'),
    path('<int:pk>/delete/', comment_delete, name='comment_delete'),
    path('user/', UserView.as_view(), name='user'),
    path('<int:pk>/profile/', UserUpdateView.as_view(), name='profile'),
    path('subscribe/', subscribe, name='subscribe'),
 ]
