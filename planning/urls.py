from django.urls import path,include
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views
from .views import WorkersUpdateView,WorkersDelete,WorkerSkillsCreate,WorkerSkillsUpdateView,WorkerSkillsModify,WorkerSkillsDelete,SkillsCreate,SkillsDelete,SkillsUpdateView,TasksUpdateView,TasksDelete

urlpatterns = [
    path('', views.home, name='planning-home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='planning/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='planning/logout.html'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Workers and skills
    path('workers/', views.workers, name='workers'),
    path('workers/add/',views.WorkersCreate.as_view(), name='workers_add'),
   	path('workers/<int:pk>/delete/',views.WorkersDelete.as_view(), name='workers_delete'),
    path('workers/<int:pk>/edit/',views.WorkersUpdateView.as_view(), name='workers_edit'),
    path('workerskills/<int:pk>/edit/',views.workerskills_edit, name='workerskills_edit'),
    path('workerskills/<int:pk>/add/',views.WorkerSkillsCreate.as_view(), name='workerskills_add'),
    path('workerskills/<int:pk>/<int:pk_ws>/modify/',views.WorkerSkillsModify.as_view(), name='workerskills_modify'),
    path('workerskills/<int:pk>/<int:pk_ws>/history/',views.workerskills_history, name='workerskills_productivity_history'),
    path('workerskills/<int:pk>/<int:pk_ws>/edit/',views.WorkerSkillsUpdateView.as_view(), name='workerskills_productivity_edit'),
    path('workerskills/<int:pk>/<int:pk_ws>/delete/',views.WorkerSkillsDelete.as_view(), name='workerskills_productivity_delete'),
    path('skills/', views.skills, name='skills'),
    path('skills/add/',views.SkillsCreate.as_view(), name='skills_add'),
    path('skills/<int:pk>/delete/',views.SkillsDelete.as_view(), name='skills_delete'),
    path('skills/<int:pk>/edit/',views.SkillsUpdateView.as_view(), name='skills_edit'),

    # Projects and tasks
    path('projects/', views.projects, name='projects'),
    path('projects/add/',views.ProjectsCreate.as_view(), name='projects_add'),
    path('projects/<int:pk>/delete/',views.ProjectsDelete.as_view(), name='projects_delete'),
    path('projects/<int:pk>/edit/',views.ProjectsUpdateView.as_view(), name='projects_edit'),
    path('projects/<int:pk>/view/',views.viewprojects, name='projects_view'),
    path('projects/<int:pk>/add/',views.TasksCreate.as_view(), name='tasks_add'),
    path('projects/<int:pk>/<int:pk_task>/edit/',views.TasksUpdateView.as_view(), name='tasks_edit'),
    path('projects/<int:pk>/<int:pk_task>/delete/',views.TasksDelete.as_view(), name='tasks_delete'),

    # Shifts, availability and planning
    path('shifts/', views.shifts, name='shifts'),
    path('shifts/add/',views.ShiftsCreate.as_view(), name='shifts_add'),
    path('shifts/<int:pk>/delete/',views.ShiftsDelete.as_view(), name='shifts_delete'),
    path('shifts/<int:pk>/edit/',views.ShiftsUpdateView.as_view(), name='shifts_edit'),

    path('availability/', views.availability, name='availability'),
    path('availability/add/',views.AvailabilityCreate.as_view(), name='availability_add'),
    path('availability/<int:pk>/delete/',views.AvailabilityDelete.as_view(), name='availability_delete'),
    path('availability/<int:pk>/edit/',views.AvailabilityUpdateView.as_view(), name='availability_edit'),

    path('planning/', views.planning, name='planning'),
    path('planning/create', views.planning_create, name='planning_create'),
    path('planning/result', views.planning_result, name='planning_result'),
    #path('about/', views.about, name='planning-about'),

]
