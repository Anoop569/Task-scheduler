from django.urls import path

from . import views

urlpatterns = [path('', views.index, name='index'),
			path("Signup.html", views.Signup, name="Signup"),
			path("SignupAction", views.SignupAction, name="SignupAction"),	    	
			path("UserLogin.html", views.UserLogin, name="UserLogin"),
			path("UserLoginAction", views.UserLoginAction, name="UserLoginAction"),
			path("ChangePassword.html", views.ChangePassword, name="ChangePassword"),
			path("ChangePasswordAction", views.ChangePasswordAction, name="ChangePasswordAction"),	 
			path("CreateTask.html", views.CreateTask, name="CreateTask"),
			path("CreateTaskAction", views.CreateTaskAction, name="CreateTaskAction"),
			path("ViewTask", views.ViewTask, name="ViewTask"),
			path("DeleteTask", views.DeleteTask, name="DeleteTask"),
			path("EditTask", views.EditTask, name="EditTask"),
			path("EditTaskAction", views.EditTaskAction, name="EditTaskAction"),
			path("MarkComplete", views.MarkComplete, name="MarkComplete"),
			path("MarkCompleted", views.MarkCompleted, name="MarkCompleted"),
			path("NotificationTime.html", views.NotificationTime, name="NotificationTime"),
			path("NotificationTimeAction", views.NotificationTimeAction, name="NotificationTimeAction"),
]