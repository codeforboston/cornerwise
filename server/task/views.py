from celery.result import AsyncResult

from shared.request import make_response, ErrorResponse


@make_response()
def task_status(req):
    try:
        task = AsyncResult(req.GET["id"])
        res = {"status": task.status.lower()}
        if task.status == "FAILURE" and isinstance(task.result, Exception):
            res["error"] = " ".join(str(x) for x in task.result.args)
        return res
    except KeyError:
        raise ErrorResponse("Missing parameter 'id'", status=400)
