# Prompts and Prompt Engineering

This document details the prompts used to create this project with AI assistance, the prompt design methodology, and the refinement process.

## Table of Contents

- [Initial PRD Prompt](#initial-prd-prompt)
- [Prompt Design Strategy](#prompt-design-strategy)
- [Prompt Refinement Process](#prompt-refinement-process)
- [Key Prompt Engineering Techniques](#key-prompt-engineering-techniques)
- [Iterative Development Prompts](#iterative-development-prompts)

---

## Initial PRD Prompt

The project started with a high-level prompt to generate a Product Requirements Document:

```
I need to build a desktop chat application in Python that:
- Has a graphical user interface (GUI) similar to Claude or ChatGPT
- Connects to a local LLM via the Ollama API
- Runs completely locally on the user's machine
- Uses a virtual environment and proper Python packaging
- Is well-tested and documented

Please create a comprehensive Product Requirements Document (PRD) for this project
that includes:
1. Project overview and goals
2. Technical requirements and constraints
3. Feature specifications
4. User interface design
5. API integration details
6. Testing strategy
7. Documentation requirements

Make it suitable for an academic assignment that demonstrates modern software
development practices.
```

### Why This Prompt Works

**Clear Constraints:**
- Specified Python as the language
- Required GUI (not CLI)
- Mandated local LLM integration via Ollama
- Emphasized local-first architecture

**Concrete Deliverables:**
- Listed 7 specific sections for the PRD
- Mentioned it's for an academic context
- Requested demonstration of best practices

**Flexibility:**
- Left room for AI to suggest specific frameworks
- Didn't over-specify implementation details
- Allowed for creative solutions within constraints

---

## Prompt Design Strategy

### 1. Hierarchical Approach

We used a **top-down strategy**:
1. **High-level PRD first** → Establish vision and requirements
2. **Architecture decisions** → Choose frameworks and structure
3. **Component implementation** → Build individual modules
4. **Integration and testing** → Connect everything together
5. **Documentation** → Comprehensive guides and comments

### 2. Incremental Specificity

Started broad, then got specific:

**Initial prompts:**
- "Build a chat application"
- "Add real-time streaming"

**Refined prompts:**
- "Implement real-time streaming using httpx's stream() method with SSE parsing"
- "Add typing indicators and progress feedback during streaming"

### 3. Context Preservation

Each prompt built on previous context:
- Referenced earlier decisions
- Asked for consistency with existing code
- Requested updates to related documentation

---

## Prompt Refinement Process

### Phase 1: Project Initialization

**Initial Prompt:**
```
Create a basic Python project structure for a desktop chat app with:
- src/ directory with modular architecture
- tests/ directory for unit tests
- requirements.txt
- README.md
- .gitignore
```

**Refinement After Feedback:**
```
Update the project structure to:
- Separate concerns: api/, core/, gui/, config/, utils/
- Add pydantic for configuration management
- Include pytest with coverage reporting
- Add detailed installation instructions for macOS
```

**Why the refinement:**
- Original was too generic
- Needed clearer separation of concerns
- Missing important dev dependencies
- Lacked platform-specific considerations

### Phase 2: Feature Development

**Initial Prompt:**
```
Implement the chat interface with Tkinter
```

**Refinement:**
```
Redesign the UI to be more modern:
- Use a card-based layout similar to modern chat apps
- Add light and dark theme support
- Include hover effects on buttons
- Use contemporary colors (indigo, emerald)
- Add a conversation history sidebar with:
  - List of saved conversations
  - Click to load any conversation
  - Delete button with confirmation
  - Auto-generated titles from first message
```

**Why the refinement:**
- User feedback requested modern design
- Assignment required Claude/ChatGPT-like interface
- Conversation history was missing from initial implementation
- Needed specific visual design guidance

### Phase 3: Testing and Documentation

**Initial Prompt:**
```
Add unit tests for the core functionality
```

**Refinement:**
```
Act as a QA engineer and create comprehensive test coverage:
- 100% coverage for ChatManager
- 100% coverage for Message/Conversation models
- 100% coverage for Settings
- High coverage (85%+) for OllamaClient
- Include edge cases and error scenarios
- Mock external API calls
- Add pytest fixtures for reusability
- Document expected test output in README
```

**Why the refinement:**
- Needed specific coverage targets
- Required proper mocking strategy
- Wanted professional QA approach
- Documentation needed actual test examples

---

## Key Prompt Engineering Techniques

### 1. Role Assignment

**Technique:** Assign specific roles to the AI

**Examples:**
- "Act as a QA engineer and generate unit tests..."
- "Act as a technical writer and create documentation..."
- "Act as a code reviewer and identify issues..."

**Benefit:** Gets domain-specific expertise and perspective

### 2. Explicit Constraints

**Technique:** Clearly state what NOT to do

**Examples:**
- "Do not use web scraping, only the Ollama API"
- "Do not commit directly to main, always use feature branches"
- "Do not use emojis unless explicitly requested"

**Benefit:** Prevents unwanted behaviors and deviations

### 3. Example-Driven Specification

**Technique:** Provide concrete examples of desired output

**Example:**
```
Update README with screenshots like this:

### Light Theme
![Light Theme](docs/images/light-theme.png)

**Features shown:**
- Conversation sidebar
- Model selector
- Theme toggle
```

**Benefit:** Ensures consistent formatting and structure

### 4. Iterative Refinement

**Technique:** Build on previous outputs with feedback loops

**Pattern:**
1. Initial implementation
2. Review and identify gaps
3. Refine with specific feedback
4. Iterate until satisfactory

**Example:**
- v1: Basic Tkinter interface
- v2: Add modern styling (feedback: looks outdated)
- v3: Add theme support (feedback: missing dark mode)
- v4: Add conversation history (feedback: can't access old chats)

### 5. Contextual Documentation

**Technique:** Request updates to related docs with code changes

**Example:**
```
When you add the conversation history feature:
1. Update the code
2. Update README Features section
3. Update ASSIGNMENT_COMPLIANCE_REPORT.md
4. Add tests for the new functionality
```

**Benefit:** Keeps documentation in sync with code

### 6. Verification Requests

**Technique:** Ask AI to verify its own work

**Examples:**
- "Run the tests and confirm all 62 pass"
- "Check for syntax errors in the modified files"
- "Verify the compliance rate calculation"

**Benefit:** Catches errors before committing

---

## Iterative Development Prompts

### Conversation History Feature (Example)

**Iteration 1 - Initial Request:**
```
I want users to be able to see their old chats in a sidebar,
like Claude or ChatGPT
```

**Iteration 2 - Clarification:**
```
Implement conversation history with:
- Left sidebar (250px) showing all saved conversations
- Click to load any conversation
- Auto-save after each message
- Persistent storage (JSON files)
- Delete functionality with confirmation
```

**Iteration 3 - Refinement:**
```
Update the sidebar to:
- Auto-generate titles from first message
- Sort by most recent first
- Show "New Chat" and "Delete" buttons
- Highlight the active conversation
- Work seamlessly with theme switching
```

**Iteration 4 - Testing:**
```
Add comprehensive tests for conversation storage:
- Save/load operations
- Title generation and truncation
- Delete functionality
- List sorting
- Edge cases (no messages, nonexistent IDs)
```

**Iteration 5 - Documentation:**
```
Update README and compliance report to reflect:
- New feature completion
- Updated compliance rate
- Screenshots showing the sidebar
```

### UI Redesign (Example)

**Iteration 1:**
```
Make the UI look more modern
```

**Iteration 2:**
```
Redesign with:
- Flat design principles
- Modern color scheme (indigo/emerald)
- Card-based layout
- Proper spacing and typography
```

**Iteration 3:**
```
Fix text contrast issues:
- New Chat button text should be black
- Theme toggle text should be black in dark mode
- Model dropdown text should be black in dark mode
```

---

## Lessons Learned

### What Worked Well

1. **Starting with PRD** - Having a clear plan prevented scope creep
2. **Incremental development** - Small, focused changes were easier to manage
3. **Consistent documentation** - Updating docs with each change kept them accurate
4. **Role-based prompts** - Asking AI to act as QA, technical writer, etc. improved output quality
5. **Feature branches** - Never committing to main made reviews easier

### What Could Be Improved

1. **Earlier testing** - Should have added tests from the beginning
2. **Design mockups** - Visual mockups before coding UI would have saved iterations
3. **Platform testing** - macOS Tkinter issues should have been caught earlier
4. **Screenshot planning** - Should have taken screenshots during development, not after

### Best Practices Discovered

1. **Be specific** - Vague prompts get vague results
2. **Provide examples** - Show desired output format
3. **Iterate** - First output is rarely perfect
4. **Verify** - Always test AI-generated code
5. **Document decisions** - Keep track of why choices were made
6. **Use constraints** - Tell AI what NOT to do
7. **Context matters** - Reference previous work for consistency
8. **Ask for completeness** - Request related updates (tests, docs, etc.)

---

## Prompt Templates for Future Use

### New Feature Template
```
Implement [FEATURE_NAME] that:
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

Technical details:
- [Implementation approach]
- [Dependencies needed]
- [Testing requirements]

Documentation needed:
- Update README [specific section]
- Add tests in [test file]
- Update compliance report if applicable
```

### Bug Fix Template
```
Fix [BUG_DESCRIPTION]:
- Current behavior: [what's happening]
- Expected behavior: [what should happen]
- Root cause: [if known]

Requirements:
- Fix the issue
- Add test to prevent regression
- Update documentation if behavior changes
```

### Code Review Template
```
Act as a code reviewer and analyze [FILE/MODULE]:
- Check for bugs and edge cases
- Verify best practices
- Suggest improvements
- Identify security issues
- Check test coverage
```

---

## Conclusion

Effective prompt engineering for this project involved:
- **Clear initial vision** via comprehensive PRD
- **Iterative refinement** based on feedback
- **Role-based prompting** for specialized tasks
- **Explicit constraints** to guide behavior
- **Contextual documentation** to maintain consistency
- **Verification loops** to ensure quality

The key insight: **AI works best as a collaborative partner, not a black box**. Providing context, examples, and feedback creates better results than one-shot prompts.
