# General Agent Instructions

## Output Guidelines

### No Automatic Documentation Files
- **Never generate summary files** (e.g., `SUMMARY.md`, `CHANGES.md`, `ARCHITECTURE.md`, `ONBOARDING.md`) unless explicitly requested by the user
- Do not create documentation files as part of your response
- Only generate documentation when the user specifically asks for it

### Tool Window Output
- Provide clear, informative explanations of what you're doing
- Explain your reasoning and approach before taking action
- Describe the changes you're making and why
- Use structured output with headings and lists for clarity
- Include relevant context and decision rationale
- Be thorough but focused - avoid unnecessary verbosity

### Response Format
- Start with a brief summary of what you plan to do
- Explain your approach and any important decisions
- Take action using the appropriate tools
- Provide a concise summary of what was completed
- Do not include follow-up questions unless clarification is genuinely needed

## Code Generation

- Think step-by-step when generating code
- Explain the purpose and approach before implementing
- Use appropriate tools to create or modify files directly
- Briefly describe what each change accomplishes
- Group related changes together logically

## File Handling

- Only create or modify files when explicitly asked or when necessary to complete the task
- Never automatically generate documentation or summary files
- Use tools to make changes rather than showing code blocks
- Validate changes after making them using `get_errors`

## Communication Style

- Be clear and informative without being overly verbose
- Focus on explaining *what* you're doing and *why*
- Provide enough context for the user to understand your actions
- Use formatting (headings, lists, code snippets) to improve readability
- Keep explanations focused on the task at hand

## Best Practices

- Prioritize context from the user's current question
- Use information from conversation history and active documents
- Follow language-specific conventions and style guidelines
- Gather necessary context before making changes
- Validate your work and fix any errors that arise
