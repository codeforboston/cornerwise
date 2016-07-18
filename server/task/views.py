from celery.result import AsyncResult

from shared.request import make_response, ErrorResponse

def task_status_dict(task_id):
    task = AsyncResult(task_id)
    res = {"status": task.status.lower()}
    if task.status == "FAILURE" and isinstance(task.result, Exception):
        res["error"] = " ".join(str(x) for x in task.result.args)
    return res


@make_response()
def task_statuses(req):
    try:
        statuses = {task_id: task_status_dict(task_id) for task_id in req.GET["ids"].split(",")}
        return {"results": statuses}
    except KeyError:
        raise ErrorResponse("Missing parameter 'ids'", status=400)


@make_response()
def task_status(req):
    try:
        return task_status_dict(req.GET["id"])
    except KeyError:
        raise ErrorResponse("Missing parameter 'id'", status=400)
