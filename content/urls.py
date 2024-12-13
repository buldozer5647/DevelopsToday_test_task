from django.urls import path

from .views import (
    SpyCatListCreateView,
    SpyCatDetailView,
    MissionListCreateView,
    MissionDetailView,
    AssignCatToMissionView,
    ChangeTargetInfoView,
    MarkTargetCompleteView,
)

urlpatterns = [
    path('cats/', SpyCatListCreateView.as_view(), name='spy-cat-list-create'),
    path('cats/<int:pk>/', SpyCatDetailView.as_view(), name='spy-cat-detail'),

    path('missions/', MissionListCreateView.as_view(), name='mission-list-create'),
    path('missions/<int:pk>/', MissionDetailView.as_view(), name='mission-detail'),
    path('missions/<int:pk>/assign_cat/', AssignCatToMissionView.as_view(), name='assign-cat-to-mission'),
    path('missions/<int:pk>/targets/<int:pk_target>/', ChangeTargetInfoView.as_view(), name='mission-detail'),
    path('missions/<int:pk>/targets/<int:pk_target>/mark_complete/', MarkTargetCompleteView.as_view(), name='mission-detail'),
]
