from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from api.models import File
from api.serializers import FileSerializer


@csrf_exempt
def file_list(request):
    files = File.objects.all()
    serializer = FileSerializer(files, many=True)
    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def file_detail(request, pk):
    try:
        snippet = File.objects.get(pk=pk)
    except File.DoesNotExist:
        return HttpResponse(status=404)

    serializer = FileSerializer(snippet)
    return JsonResponse(serializer.data)


@csrf_exempt
def file_upload(request):
    data = JSONParser().parse(request)
    serializer = FileSerializer(File, data=data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data)
    return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def file_download(request, pk):
    pass
