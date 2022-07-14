from django.urls import include, path
from rest_framework import routers

from .views import (AuthenticationViewSet, CategoryViewSet, CommentViewSet,
                    GenresViewSet, ReviewViewSet, TitlesViewSet, UserViewSet)

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1.register(r'titles/(?P<title_id>\d+)/reviews',
                   ReviewViewSet, basename='review')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews/'
                   r'(?P<review_id>\d+)/comments',
                   CommentViewSet, basename='comment')
router_v1.register('users', UserViewSet)
router_v1.register('categories', CategoryViewSet)
router_v1.register('genres', GenresViewSet)
router_v1.register('titles', TitlesViewSet, basename='titles')
router_v1.register('auth', AuthenticationViewSet,
                   basename='get_confirmation_code')

urlpatterns = [
    path('v1/', include('djoser.urls.jwt')),
    path('v1/', include(router_v1.urls)),
]
