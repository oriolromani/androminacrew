from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Task
from .serializers import TaskSerializer


class TaskList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
        Retrieve the tasks according to the user.
        - admin user: all tasks
        - company user: the taks of the company
        - user: the tasks proposed to the user

        """
        if request.user.is_staff:
            tasks = Task.objects.all()
        else:
            try:
                company = request.user.company
                tasks = Task.objects.filter(company=company)
            except AttributeError:
                tasks = request.user.user_tasks.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
