1. Why nest_asyncio==1.6.0?

Since our MCP and backend applications use asynchronous functions, sometimes an asyncio event loop is already running. nest_asyncio allows us to run another asyncio operation inside the existing event loop without causing an event-loop conflict. It is especially useful in environments like Jupyter notebooks.

Simple meaning:

Existing event loop
       ↓
MCP / Backend async function
       ↓
nest_asyncio allows nested execution

⚠️ nest_asyncio is not required just because we have multiple async functions.

2. Why does MCP use async Python functions?

When an MCP server receives multiple requests, some requests may involve long-running I/O operations such as LLM calls, database queries, or external API calls. If we use synchronous functions, the server may remain blocked while waiting for the operation to complete. By using async functions with await, the event loop can handle other requests while one request is waiting for I/O. This improves concurrency and responsiveness.

Simple meaning:

Request 1 → LLM API → waiting
                    ↓
              Event loop
                    ↓
Request 2 → Database/API → handled
                    ↓
Request 1 → Result received

Instead of saying:

❌ "Multiple requests run in parallel as event loops."

Say:

✅ "Multiple requests can be handled concurrently by the event loop, especially while they are waiting for I/O operations."