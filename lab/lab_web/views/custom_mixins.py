from rest_framework.response import Response
from rest_framework import status


class CreateListModelMixin:

    def create(self, request, *args, **kwargs):
        """
            Create a list of model instances if a list is provides or a
            single model instance otherwise.
        """
        data = request.data
        if isinstance(data, list):
            serializer = self.get_serializer(data=request.data, many=True)
        else:
            serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)
