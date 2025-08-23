# Tasks - optimistic locking

## Optimistic lock conflict
Tags: tasks, optimistic-lock

* Generate random credentials
* Register user via API (expect success)
* Login with credentials (expect success)
* Create task with title "lock-test" and description "lock-test"
* Update task with current version (expect success)
* Attempt update with stale version (expect 409)