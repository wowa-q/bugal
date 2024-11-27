from home import views
from django.urls import path


app_name = 'home' # dieser Name wird dann in den Templates genutzt

urlpatterns = [
    path('', views.BugalHomeView.as_view(), name='home')

    # path('schools/', views.SchoolListView.as_view(),name='list'),
    # path('schools/<int:pk>/', views.SchoolDetailView.as_view(), name='school_detail'),
    # path('create/', views.SchoolCreateView.as_view(), name='create'),
    # path('update/<int:pk>/', views.SchoollUpdateView.as_view(),name='update'),
    # path('delete/<int:pk>/', views.SchoolDeleteView.as_view(),name='delete'),
]
