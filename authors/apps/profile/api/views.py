from rest_framework import status
from rest_framework.generics import (
  ListAPIView,
  RetrieveUpdateAPIView,
  RetrieveAPIView,
  RetrieveUpdateDestroyAPIView,

)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.permissions import (
 IsAuthenticatedOrReadOnly,
 IsAuthenticated
)
from rest_framework.response import Response
from .serializers import (
    TABLE, ProfileListSerializer, ProfileUpdateSerializer, User,
)
from ...core.permissions import IsOwnerOrReadOnly
from django.contrib.sites.shortcuts import get_current_site

def get_profile(username):
    try:
        profile = TABLE.objects.get(user__username=username)
    except User.DoesNotExist:
        serializers.ValidationError('User does not exist.')
    return profile


def get_current_profile(request):
    user = request.user
    return user.profile


class ProfileListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileListSerializer
    queryset = TABLE.objects.all()


class ProfileDetailAPIView(RetrieveAPIView):
    queryset = TABLE.objects.all()
    serializer_class = ProfileListSerializer
    lookup_field = 'user__username'

class MyProfileDetailAPIView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileListSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user.profile)

        return Response(serializer.data, status=status.HTTP_200_OK)

class ProfileUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = TABLE.objects.all()
    serializer_class = ProfileUpdateSerializer
    lookup_field = 'user__username'


class FollowProfilesAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, username):
        '''Follow a user'''
        try:
            #check if user exists
            user = User.objects.get(username=username)
        except:
            message = {"error": "User {} does not exists".format(username)}
            return Response(message, status=status.HTTP_404_NOT_FOUND)

        #ensure username has not been followed before
        current_profile = get_current_profile(request)
        is_following = current_profile.following(profile=current_profile)
        if username in str(is_following):
            message = {"error": "You cannot follow someone that you already follow"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        #ensure you don't follow yourself
        current_username = User.objects.get(email=request.user).username
        if current_username == username:
            message = {'error': 'You cannot follow yourself.'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        #follow
        profile = get_profile(username)
        current_profile.follow(profile)
        message = {"success": "User {} followed successfully".format(username)}
        return Response(message, status=status.HTTP_200_OK)


    def delete(self, request, username):
        '''unfollow a user'''
        # check if user exists
        try:
            user = User.objects.get(username=username)
        except:
            message = {"error": "User {} does not exists".format(username)}
            return Response(message, status=status.HTTP_404_NOT_FOUND)

        # check if you are following that user
        current_profile = get_current_profile(request)
        following = current_profile.following(profile=current_profile)
        if username not in str(following):
            message = {"error": "You cannot unfollow someone that you don't follow"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        # unfollow that user
        profile = get_profile(username)
        current_profile.unfollow(profile=profile)
        message = {"success": "User {} unfollowed successfully".format(username)}
        return Response(message, status=status.HTTP_200_OK)


class ListFollowingProfilesAPIView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, username):
        '''get following'''
        profile = get_profile(username)
        following = profile.following(profile=profile)
        data = []
        for i in following:
            data.append(i.user.username)
        message = {"following": data}
        return Response(message, status=status.HTTP_200_OK)


class ListFollowersProfilesAPIView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, username):
        '''get followers'''
        profile = get_profile(username)
        followers = profile.get_followers(profile=profile)
        data = []
        for i in followers:
            data.append(i.user.username)
        message = {"followers": data}
        return Response(message, status=status.HTTP_200_OK)
