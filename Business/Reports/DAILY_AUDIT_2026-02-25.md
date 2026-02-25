# Daily Audit Report — 2026-02-25

> Generated: 2026-02-25T09:05:12Z  
> Source: `Logs/*.json`

---

## Summary

| Metric | Value |
|--------|-------|
| Total events | **176** |
| Successes | 171 |
| Failures | 5 |
| Success rate | ✅ **97.2%** |

---

## Activity by Server

| Server | Events |
|--------|--------|
| `mcp_file_ops` | 85 |
| `gold_agent` | 25 |
| `mcp_audit_ops` | 15 |
| `mcp_router` | 14 |
| `mcp_calendar_ops` | 10 |
| `domain_router` | 8 |
| `social_mcp_stub` | 8 |
| `odoo_mcp_stub` | 6 |
| `ceo_briefing` | 5 |

---

## Top Actions

| Action | Count |
|--------|-------|
| `read_task` | 53 |
| `list_tasks` | 25 |
| `get_current_week` | 10 |
| `get_recent_actions` | 10 |
| `write_task` | 6 |
| `loop_complete` | 5 |
| `get_all_domain_tasks` | 5 |
| `agent_start` | 5 |
| `loop_start` | 5 |
| `get_action_summary` | 5 |
| `agent_complete` | 5 |
| `save_briefing` | 5 |
| `classify_task` | 3 |
| `task_error` | 3 |
| `social_post_facebook_dry_run` | 2 |

---

## Hourly Distribution

| Hour (UTC) | Events |
|------------|--------|
| 02:00 | 25 █████████████████████████ |
| 04:00 | 26 ██████████████████████████ |
| 05:00 | 61 ████████████████████████████████████████ |
| 06:00 | 25 █████████████████████████ |
| 07:00 | 25 █████████████████████████ |
| 09:00 | 14 ██████████████ |

---

## Errors

**5 error(s) detected:**

- `2026-02-25T04:16:17.798324+00:00` | `gold_agent` | `openai_config_missing` | {'reason': 'openai library missing'}
- `2026-02-25T05:50:10.821908+00:00` | `gold_agent` | `task_error` | {'name': 'facebook_post_demo.md', 'error': "Error code: 429 - {'error': {'message': 'You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.', 'type': 'insufficient_quota', 'param': None, 'code': 'insufficient_quota'}}", 'traceback': 'Traceback (most recent call last):\n  File "/home/runner/work/AI_Employee_Vault_Gold_Hackathon0/AI_Employee_Vault_Gold_Hackathon0/gold_agent.py", line 179, in process_task\n    summary, status = openai_summarize(prompt)\n                      ^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/home/runner/work/AI_Employee_Vault_Gold_Hackathon0/AI_Employee_Vault_Gold_Hackathon0/gold_agent.py", line 124, in openai_summarize\n    resp = client.chat.completions.create(\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/openai/_utils/_utils.py", line 286, in wrapper\n    return func(*args, **kwargs)\n           ^^^^^^^^^^^^^^^^^^^^^\n  File "/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/openai/resources/chat/completions/completions.py", line 1204, in create\n    return self._post(\n           ^^^^^^^^^^^\n  File "/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/openai/_base_client.py", line 1297, in post\n    return cast(ResponseT, self.request(cast_to, opts, stream=stream, stream_cls=stream_cls))\n                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/openai/_base_client.py", line 1070, in request\n    raise self._make_status_error_from_response(err.response) from None\nopenai.RateLimitError: Error code: 429 - {\'error\': {\'message\': \'You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.\', \'type\': \'insufficient_quota\', \'param\': None, \'code\': \'insufficient_quota\'}}\n'}
- `2026-02-25T05:50:14.707270+00:00` | `gold_agent` | `task_error` | {'name': 'facebook_post_demo.md', 'error': "Error code: 429 - {'error': {'message': 'You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.', 'type': 'insufficient_quota', 'param': None, 'code': 'insufficient_quota'}}", 'traceback': 'Traceback (most recent call last):\n  File "/home/runner/work/AI_Employee_Vault_Gold_Hackathon0/AI_Employee_Vault_Gold_Hackathon0/gold_agent.py", line 179, in process_task\n    summary, status = openai_summarize(prompt)\n                      ^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/home/runner/work/AI_Employee_Vault_Gold_Hackathon0/AI_Employee_Vault_Gold_Hackathon0/gold_agent.py", line 124, in openai_summarize\n    resp = client.chat.completions.create(\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/openai/_utils/_utils.py", line 286, in wrapper\n    return func(*args, **kwargs)\n           ^^^^^^^^^^^^^^^^^^^^^\n  File "/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/openai/resources/chat/completions/completions.py", line 1204, in create\n    return self._post(\n           ^^^^^^^^^^^\n  File "/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/openai/_base_client.py", line 1297, in post\n    return cast(ResponseT, self.request(cast_to, opts, stream=stream, stream_cls=stream_cls))\n                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/openai/_base_client.py", line 1070, in request\n    raise self._make_status_error_from_response(err.response) from None\nopenai.RateLimitError: Error code: 429 - {\'error\': {\'message\': \'You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.\', \'type\': \'insufficient_quota\', \'param\': None, \'code\': \'insufficient_quota\'}}\n'}
- `2026-02-25T05:50:18.257447+00:00` | `gold_agent` | `task_error` | {'name': 'facebook_post_demo.md', 'error': "Error code: 429 - {'error': {'message': 'You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.', 'type': 'insufficient_quota', 'param': None, 'code': 'insufficient_quota'}}", 'traceback': 'Traceback (most recent call last):\n  File "/home/runner/work/AI_Employee_Vault_Gold_Hackathon0/AI_Employee_Vault_Gold_Hackathon0/gold_agent.py", line 179, in process_task\n    summary, status = openai_summarize(prompt)\n                      ^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/home/runner/work/AI_Employee_Vault_Gold_Hackathon0/AI_Employee_Vault_Gold_Hackathon0/gold_agent.py", line 124, in openai_summarize\n    resp = client.chat.completions.create(\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/openai/_utils/_utils.py", line 286, in wrapper\n    return func(*args, **kwargs)\n           ^^^^^^^^^^^^^^^^^^^^^\n  File "/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/openai/resources/chat/completions/completions.py", line 1204, in create\n    return self._post(\n           ^^^^^^^^^^^\n  File "/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/openai/_base_client.py", line 1297, in post\n    return cast(ResponseT, self.request(cast_to, opts, stream=stream, stream_cls=stream_cls))\n                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/opt/hostedtoolcache/Python/3.11.14/x64/lib/python3.11/site-packages/openai/_base_client.py", line 1070, in request\n    raise self._make_status_error_from_response(err.response) from None\nopenai.RateLimitError: Error code: 429 - {\'error\': {\'message\': \'You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.\', \'type\': \'insufficient_quota\', \'param\': None, \'code\': \'insufficient_quota\'}}\n'}
- `2026-02-25T05:50:19.620892+00:00` | `gold_agent` | `max_retries_reached` | {'name': 'facebook_post_demo.md', 'retries': 3}

---

*AI Employee Vault — Gold Tier | Daily Audit Runner*
