# Tasks - API (create, fetch, delete, update)

## Scenario: Create and fetch (session check)
* Generate random credentials
* Register user via API (expect success)
* Login with credentials (expect success)
* Create task with title "session-test" and description "session-test description"
* Fetch task by id and check title is "session-test"

## Scenario: Delete twice (repeat delete)
* Generate random credentials
* Register user via API (expect success)
* Login with credentials (expect success)
* Create task with title "to-delete" and description "will be deleted"
* Delete task (expect success)
* Delete task again (expect not found)
* Fetch deleted task by id (expect not found)

## Scenario: Update title and set status
* Generate random credentials
* Register user via API (expect success)
* Login with credentials (expect success)
* Create task with title "update-test" and description "update description"
* Update task title to "update-test-new" and check updated
* Set task status to "done"

## Scenario: Create without description and cleanup
* Generate random credentials
* Register user via API (expect success)
* Login with credentials (expect success)
* Create task with title "no-desc" and description ""
* Fetch task by id and check title is "no-desc"
* Delete task (expect success)
