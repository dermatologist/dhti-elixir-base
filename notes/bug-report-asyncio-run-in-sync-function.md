# Bug Report: asyncio.run() in Synchronous Functions Causes Event Loop Conflicts

## Issue Summary

**Severity**: High  
**Location**: `src/dhti_elixir_base/agent.py`  
**Lines Affected**: 91, 104, 109  
**Branch**: feature/auto-bug-fix-1

## Description

The `BaseAgent` class in `agent.py` uses `asyncio.run()` within synchronous methods (`has_tool()` and `get_agent_response()`). This pattern causes critical runtime errors when:

1. The code is called from within an existing event loop (e.g., FastAPI, asyncio applications)
2. Multiple concurrent calls are made, causing event loop conflicts
3. The application is already running under an asyncio context

### Affected Methods

#### 1. `has_tool()` (Line 91)
```python
def has_tool(self) -> bool:
    """Check if the agent has any tools."""
    try:
        _tools = asyncio.run(self.client.list_tools())  # BUG: asyncio.run in sync function
        return bool(_tools)
    except Exception as e:
        logger.error(f"Error checking tools: {e}")
        return False
```

#### 2. `get_agent_response()` (Lines 104, 109)
```python
def get_agent_response(self, context: str) -> str:
    if self.llm is None:
        raise ValueError("llm must not be None when initializing the agent.")
    result = "Agent encountered an error while processing your request."
    try:
        # if self.tools is an empty list, load tools from MCP
        if not self.tools:
            _tools = asyncio.run(self.client.list_tools())  # BUG: asyncio.run in sync function
        else:
            _tools = self.tools
        _agent = create_agent(model=self.llm, tools=_tools, system_prompt=self.prompt)

        result = asyncio.run(_agent.ainvoke(  # BUG: asyncio.run in sync function
            {"messages": [{"role": "user", "content": context}]}
        ))
        ai_message = result["messages"][-1].content
        return str(ai_message)
    except Exception as e:
        logger.error(f"Error in agent processing: {e}")
        return str(result)
```

## Impact

- **RuntimeError**: "This event loop is already running" when called from async context
- **Application Crashes**: In web frameworks like FastAPI that manage their own event loops
- **Concurrency Issues**: Potential deadlocks or race conditions in multi-threaded environments
- **Resource Leaks**: Improper event loop teardown can leak resources

## Root Cause

`asyncio.run()` is designed to create a new event loop, run a coroutine, and then close the loop. It cannot be called:
- From within an already running event loop
- In nested contexts
- In synchronous methods that might be called from async code

## Fix Plan

### Strategy: Convert to Async Methods

The cleanest solution is to convert the synchronous methods to async methods and provide both sync and async variants:

1. **Rename existing methods to async versions**:
   - `has_tool()` → `ahas_tool()`
   - `get_agent_response()` → `aget_agent_response()`

2. **Create synchronous wrappers** that use `asyncio.run()` only when no event loop is running:
   - Keep `has_tool()` as sync wrapper
   - Keep `get_agent_response()` as sync wrapper
   - Use `asyncio.get_event_loop().run_until_complete()` pattern or check for running loop

3. **Implementation approach**:
   ```python
   import asyncio
   
   def has_tool(self) -> bool:
       """Check if the agent has any tools (sync wrapper)."""
       try:
           # Check if we're in an event loop
           loop = asyncio.get_running_loop()
           if loop:
               # We're in an async context, raise helpful error
               raise RuntimeError(
                   "has_tool() called from async context. Use ahas_tool() instead."
               )
           return asyncio.run(self.ahas_tool())
       except Exception as e:
           logger.error(f"Error checking tools: {e}")
           return False
   
   async def ahas_tool(self) -> bool:
       """Check if the agent has any tools (async version)."""
       try:
           _tools = await self.client.list_tools()
           return bool(_tools)
       except Exception as e:
           logger.error(f"Error checking tools: {e}")
           return False
   ```

### Alternative: Use run_in_executor

For cases where we must maintain sync API, we could use `loop.run_in_executor()` to run the async code in a thread pool, avoiding event loop conflicts.

## Testing Requirements

1. Test calling `has_tool()` from:
   - Synchronous context (should work)
   - Async context (should provide clear error or work correctly)
   
2. Test calling `get_agent_response()` from:
   - Synchronous context (should work)
   - Async context (should provide clear error or work correctly)

3. Test concurrent calls to ensure no race conditions

4. Test in FastAPI/async web framework context

## Files to Modify

- `src/dhti_elixir_base/agent.py` - Main fix
- Potentially update any callers if API changes are made

## Priority

**High** - This bug will cause application failures in production when:
- Used with FastAPI or other async web frameworks
- Called from async contexts
- Used in concurrent/multi-threaded environments
