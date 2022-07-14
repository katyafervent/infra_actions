from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Categories, Genres, Review, Title
from users.models import User
from users.tokens import ConfirmationCodeTokenGenerator

from .filters import TitlesFilter
from .permissions import (IsAdmin, IsAdminUserOrReadOnly,
                          IsAuthorOrReadOnlyPermission)
from .serializers import (AdminSerializer, CategoriesSerializer,
                          CommentSerializer, ConfirmationCodeSerializer,
                          GenresSerializer, JwtTokenSerializer,
                          ReviewSerializer, TitleListSerializer,
                          TitleWriteSerializer, UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """Viewset for users/."""

    queryset = User.objects.all().order_by('id')
    serializer_class = AdminSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    pagination_class = PageNumberPagination

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        """
        View for users/me. Allows any authenticated user access and
        patch it's profile.
        """
        user = User.objects.get(username=request.user.username)
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthenticationViewSet(viewsets.GenericViewSet):
    """Viewset for registering and authenticating users."""

    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        """Returns serializer class depending on which view is used."""
        if self.action == 'send_confirmation_code':
            return ConfirmationCodeSerializer
        return JwtTokenSerializer

    def send_email(self, user: User):
        """Sends confirmation code to user."""
        token_generator = ConfirmationCodeTokenGenerator()
        subject = 'Код подтвеждения'
        body = '''
        Ваш код для авторизации на сайте YaMDB: {confirmation_code}
        Ваше имя пользователя: {username}'''
        from_email = 'noreply@yamdb.ru'
        email = user.email
        username = user.username
        confirmation_code = token_generator.make_token(user)
        confirmation_email = EmailMessage(
            subject=subject,
            body=body.format(
                confirmation_code=confirmation_code, username=username),
            from_email=from_email,
            to=[email],
        )
        confirmation_email.send()

    @action(
        methods=['post'], detail=False, url_path='signup', url_name='signup',
    )
    def send_confirmation_code(self, request):
        """
        View for signing up new user. If user was already created
        sends new email with confirmation code.
        """
        try:
            user = User.objects.get(
                username=request.data.get('username'),
                email=request.data.get('email'),
            )
        except User.DoesNotExist:
            pass
        else:
            self.send_email(user)
            data = {'email': user.email, 'username': user.username}
            return Response(data=data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data['email']
            username = serializer.validated_data['username']
            user, created = User.objects.get_or_create(
                username=username, email=email,
            )
            self.send_email(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='token', url_name='token')
    def get_jwt_token(self, request):
        """View for refreshing jwt access token for registered user."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            username = serializer.validated_data.get('username')
            user = get_object_or_404(User, username=username)
            token = RefreshToken.for_user(user)
            return Response(
                data={'access': str(token.access_token)},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    lookup_field = 'slug'
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def retrieve(self, request, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GenresViewSet(viewsets.ModelViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def destroy(self, request, **kwargs):
        slug = self.kwargs.get('pk')
        Genres.objects.filter(slug=slug).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TitlesViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUserOrReadOnly,)
    queryset = Title.objects.all()
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitlesFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleListSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Api endpoint has access to SAFE_METHODS
    without registering.
    """
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrReadOnlyPermission,)

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, pk=title_id)
        return title.review_title.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(title=title,
                        author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Api endpoint has access to SAFE_METHODS
    without registering.
    """
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnlyPermission,)

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        review_id = self.kwargs.get("review_id")
        review = Review.objects.get(pk=review_id,
                                    title_id=title_id)
        return review.review_comment.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review_id = get_object_or_404(Review, pk=review_id)
        serializer.save(review_id=review_id,
                        author=self.request.user)
