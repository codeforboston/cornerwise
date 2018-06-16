/**
 * JavaScript for user pages, admin, etc. For the single page application, see
 * main.js
 */

function wait(ms, fn) {
    var deferred = $.Deferred();

    setTimeout(function() {
        deferred.resolve(null);
    }, ms);

    return deferred.then(fn);
}

function monitorTasks(task_ids, checks, fn, delay) {
    if (checks <= 0 || !task_ids.length)
        return null;

    return $.getJSON("/task/statuses?ids=" + task_ids.join(","))
        .then(function(results) {
            var complete = {};
            $.each(results.results, function(task_id, status) {
                if (status.status !== "pending") {
                    fn(task_id, status);
                    complete[task_id] = true;
                }
            });

            var next_ids = $.grep(task_ids, function(task_id) { return !complete[task_id]; });

            return wait(delay, function() {
                return monitorTasks(next_ids, checks-1, fn, delay*1.5);
            });
        });
}

$(function() {
    (function() {
        var task_alerts = {}, task_ids = [];
        $(".task-pending").each(function(_i, task_alert) {
            var task_id = task_alert.getAttribute("data-taskid");

            if (task_id) {
                task_alerts[task_id] = this;
                task_ids.push(task_id);
            }
        });

        monitorTasks(task_ids, 10, function(task_id, result) {
            var elt = task_alerts[task_id];

            $(elt)
                .addClass(result.status === "failure" ?
                          "task-failure" : "task-success")
                .removeClass("task-pending");
            delete task_alerts[task_id];
        }, 2000);
    })();
});
