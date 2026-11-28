Perform a comprehensive senior-level code review of this pull request.

Review the changes from the perspective of:
- Correctness and potential bugs
- Logic errors and edge cases
- Performance and scalability
- Security vulnerabilities
- Reliability and fault tolerance
- Concurrency/threading/async issues
- Error handling and logging
- API and contract compatibility
- Architecture and design quality
- Maintainability and readability
- Test coverage and test quality
- Documentation and developer experience
- Compliance with project conventions and best practices

For every issue found:
1. Specify severity: Critical, High, Medium, or Low.
2. Explain why it is a problem.
3. Reference the affected file(s) and code section(s).
4. Provide a concrete recommendation or code example for fixing it.

Also identify:
- Potential regressions
- Missing tests
- Breaking changes
- Technical debt introduced by this PR
- Opportunities for simplification or refactoring

At the end, provide a final verdict in the following format:

## Review Summary
- Critical Issues: X
- High Issues: X
- Medium Issues: X
- Low Issues: X

## Approval Decision
Choose exactly one:
- ✅ APPROVED
- ⚠️ APPROVED WITH RECOMMENDATIONS
- ❌ CHANGES REQUIRED

If the PR should not be approved, clearly state:

"❌ CHANGES REQUIRED"

and provide a numbered list of all required changes that must be addressed before approval.

Be strict and production-oriented. Do not assume code is correct simply because tests pass. Look for hidden bugs, race conditions, security concerns, maintainability problems, and long-term operational risks.