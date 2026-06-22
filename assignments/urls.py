from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
    path('assign/<int:ticket_id>/', views.assign_ticket, name='assign'),
    path('workload/', views.workload_view, name='workload'),
]
