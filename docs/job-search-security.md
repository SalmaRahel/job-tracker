Job search security notes

The user asks a question, Gemini writes SQL, and we run it read-only.
We do not trust Gemini, the question, or the data in the rows.

Validator: one SELECT only, on the job table, with 8 allowed columns and a short list of safe functions.
Read-only role: job_search_ro can only SELECT those 8 columns, so it cannot write or read other tables.
RLS: the database only returns rows where user_id matches the logged-in user.
Timeout and row cap: 3 seconds and 50 rows at most.
Untrusted data: the question and the rows go in labelled blocks, and the prompt says they are data, not instructions. This lowers the risk but is not a guarantee.

Known gap: set_config can switch the user.
RLS reads the setting app.user_id, and any role can call set_config on it.
A test showed that a query doing this can read another user's rows at the database level.
The validator blocks set_config, because functions are an allowlist, so the endpoint is safe for now.
So the validator is required. RLS alone is not enough.
An xfail test records this gap.
Fix later: check a signed user id in the policy, or stop this role from calling set_config.
