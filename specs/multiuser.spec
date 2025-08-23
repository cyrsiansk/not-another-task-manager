# Tasks - multi-user and auth

## User isolation: other user cannot access tasks
Tags: tasks, security

* Generate random credentials
* Register user via API (expect success)
* Login with credentials (expect success)
* Create task with title "secret-task" and description "secret-description"
* Create and login as another user
* Attempt to fetch the first user's task by id (expect not found)

## Unauthorized access to protected endpoint
Tags: auth, security

* Send request to GET /tasks without token (expect 401)