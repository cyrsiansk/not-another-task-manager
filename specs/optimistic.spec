# Tasks - optimistic locking

## Optimistic lock conflict
Tags: tasks, optimistic-lock

* Create task with title "lock-test" and description "lock-test"
* Update task with current version (expect success)
* Attempt update with stale version (expect 409)