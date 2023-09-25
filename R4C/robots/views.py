from json import loads

from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Robot
from .validators import validate_robot


@csrf_exempt
def create_robot(request):
    """функция создания данных для робота."""
    data = validate_robot(loads(request.body))
    try:
        model = data.get('model')
        version = data.get('version')
        serial = f'{model}-{version}'
        created = data.get('created')
        robot, create = Robot.objects.get_or_create(
            model=model,
            version=version,
            serial=serial,
            created=created,
        )
    except Exception:
        return HttpResponseBadRequest(data)
    if create:
        robot_json = robot.__dict__
        robot_json.pop('_state')
        return JsonResponse(robot_json)
    return HttpResponseBadRequest('Данный робот был создан ранее.')
