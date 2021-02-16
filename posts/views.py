from django.shortcuts import render
from rest_framework import generics, permissions, mixins, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from posts.models import Post, Vote
from posts.serializers import PostSerializer, VoteSerializer

'''LISTE DE POSTES'''
class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    '''CREE UNE POST PAR L'UTILISATEUR CONNECTE'''
    def perform_create(self, serializer):
        serializer.save(poster=self.request.user)

'''DELTE PAR LEUR CREACTEUR OU LIRE LA POSTE '''
class PostRetrieveDestroyAPIView(generics.RetrieveDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    '''DELETE LE POST PAR SON CREATEUR SEULE OU LIRE PAR N'IMPORT QUI !'''
    def delete(self, request, *args, **kwargs):
        post= Post.objects.filter(pk=kwargs['pk'],poster=self.request.user)
        if post.exists():
            return self.destroy(request,*args,**kwargs)
        else:
            raise ValidationError('This isn\'t your post to delete, BRUH!')

'''CREATION DE VOTE'''
class VoteCreate(generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    '''RETURN UNE LISTE DE TOUTE LES VOTES SUR LES POSTES D'UTILISATEUR CONECTE'''
    def get_queryset(self):
        user = self.request.user
        post = Post.objects.get(pk=self.kwargs['pk'])
        return Vote.objects.filter(voter=user, post=post)
    '''CREE UNE VOTE PAR L'UTILISATEUR CONNECTE SUR N'IMPORT POST'''
    def perform_create(self, serializer):
        if self.get_queryset().exists():
            raise ValidationError('You have already voted for this post :)')
        serializer.save(voter=self.request.user, post=Post.objects.get(pk=self.kwargs['pk']))
    '''DELETE VOTE'''
    def delete(self,request,*args,**kwargs):
        if self.get_queryset().exists():
            self.get_queryset().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError('You never voted this post .. silly!')

