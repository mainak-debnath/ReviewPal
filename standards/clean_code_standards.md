# 🛠️ General Principles

1.  Adhere to established coding standards.
2.  Embrace simplicity — avoid unnecessary complexity.
3.  Improve the codebase as you go. Leave it better than you found it.
4.  Dig deep to identify the actual root cause of issues.

# 🎨 Design Guidelines

1.  Store configuration at higher abstraction layers.
2.  Use polymorphism instead of branching with if/else or switch statements.
3.  Avoid making systems overly configurable.
4.  Leverage dependency injection for managing dependencies.
5.  Respect the Law of Demeter — interact only with direct collaborators.

# 🧠 Code Clarity Tips

1.  Stay consistent in coding patterns and practices.
2.  Name variables clearly to explain their purpose.
3.  Use specific value objects instead of generic primitives.
4.  Don’t rely on hidden dependencies across class methods.
5.  Rewrite negative conditions as positives for better readability.

# 🔤 Naming Conventions

1.  Pick names that clearly convey their purpose.
2.  Ensure names make meaningful distinctions.
3.  Use names that are easy to read and pronounce.
4.  Choose names that can be easily found with search tools.
5.  Replace unexplained numbers with well-named constants.
6.  Avoid prefixing with types or roles (no txt, arg, str, etc.).

# 🔧 Function Best Practices

1.  Keep functions short and focused.
2.  Ensure each function does only one thing.
3.  Name functions to clearly express their behavior.
4.  Reduce the number of parameters whenever possible.
5.  Avoid hidden effects — functions should be transparent in what they do.
6.  Eliminate boolean flags; create separate functions for separate behaviors.

# 🧱 Source Structure Principles

1.  Separate distinct concerns vertically in the file.
2.  Group related logic closely together.
3.  Declare variables where they are first used.
4.  Place dependent functions near each other.
5.  Keep similar functions close in the file.
6.  Order functions top-down in terms of their dependencies.
7.  Keep lines concise and readable.
8.  Avoid aligning code horizontally.
9.  Use whitespace to group related code and separate unrelated sections.
10. Maintain clean indentation without forcing it.

# 🧩 Objects & Data Design

1.  Encapsulate internal details — expose only what’s needed.
2.  Choose pure data models or pure behavior — avoid mixing the two.
3.  Keep objects compact and focused.
4.  Each object should represent a single concept.
5.  Limit the number of internal variables.
6.  Base classes should not depend on or make assumptions about subclasses.
7.  Replace flags with specialized methods rather than passing control signals.
8.  Favor instance methods over static methods when object behavior is involved.

# 🧪 Testing Principles

1.  Focus each test on a single responsibility.
2.  Make tests clear and easy to understand.
3.  Ensure tests are independent from one another.
4.  Tests should be repeatable and produce consistent results.

# 🚨 Code Smell Indicators

1.  **Too rigid** — small changes ripple through many parts of the code.
2.  **Too fragile** — a minor change breaks unrelated areas.
3.  **Hard to reuse** — the code is tightly coupled and difficult to extract.
4.  **Overcomplicated** — the solution is more complex than needed.
5.  **Duplicate logic** — similar code appears in multiple places.
6.  **Unclear intent** — the code is difficult to follow and understand
