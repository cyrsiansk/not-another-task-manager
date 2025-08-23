# Auth

## Successful registration and retrieval
Tags: successful, auth

* Generate random credentials
* Register user via API (expect success)
* Login with credentials (expect success)
* Fetch tasks for the user (expect success)


## Registration validation errors
Tags: failed, auth

* Generate random credentials
* Attempt to register user via API with invalid password (expect failure)
* Attempt to login with those invalid credentials (expect failure)


## Duplicate registration (same data)
Tags: failed, auth

* Generate random credentials
* Register user via API (expect success)
* Register same user again via API (expect failure)


## Duplicate registration (data update check)
Tags: failed, auth

* Generate random credentials
* Register user via API (expect success)
* Attempt to register same email with a different password (expect failure)
* Attempt to login with the different password (expect failure)
* Login with original password (expect success)
* Fetch tasks for the user (expect success)
