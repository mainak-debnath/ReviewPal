# Angular Development Standards & Conventions

This document outlines recommended coding standards and practices for Angular projects. Following these guidelines promotes consistency, readability, and maintainability across the codebase.

## 1\. Project Structure & File Organization

We advocate for a **feature-centric architecture**, where application sections are encapsulated in their own folders.

- **Feature Modules:** Each major application feature should reside in its dedicated folder and possess its own Angular feature module.
- **Routing Segregation:** Keep feature-specific routes contained within their respective modules, minimizing cross-feature routing.
- **Lazy Loading Focus:** Design the structure with lazy-loading in mind to optimize initial bundle size.
- **Module Contents:** Each feature module typically includes:

  - A primary **feature module file** (e.g., feature.module.ts).
  - A **feature-level routing file** for managing internal routes (e.g., feature-routing.module.ts).
  - A pages or views directory for **container components** (components loaded directly by routes).
  - A components or presentational directory for **reusable UI components** specific to the module.
  - Dedicated folders for module-specific services, models, enums, directives, and pipes (as needed).
  - An optional state folder if using NgRx or similar state management.

- **Single-Purpose Files:** Ensure each file is dedicated to a single concern (e.g., one component per file, one service per file). This extends to enums, which should also reside in their own files.
- **Refactoring Large Files:** Don't hesitate to break down large files into smaller, more manageable units when logical.
- **Generic Components:** Create separate folders for widely reusable components.
- **Sub-folder Rule:** Consider creating sub-folders if a directory grows to seven or more files.
- **File Naming:** All file names must use **kebab-case** (e.g., my-cool-component.component.ts).

## 2\. TypeScript Guidelines

Adhere to clear, concise, and consistent TypeScript usage.

- **Function Length:** Keep functions and methods concise and focused. Break them into smaller, logical units when appropriate.
- **Quotes:** Prefer **single quotes** for strings.
- **Explicit Typing:** Always explicitly declare types for properties and variables, unless TypeScript can clearly infer the type during creation.

## 3\. Component & Selector Conventions

Specific rules for Angular components and their selectors.

- **Reusable Component Selector Prefix:** Presentational (reusable) components should have selectors prefixed with mri-ph (e.g., ).
- **Container Component Selectors:** Selectors are generally not required for container components (those in pages or views folders) as they are typically loaded via routing.
- **Member Order (within a class):** Maintain a consistent order for class members. Within each category, group members by accessibility: public, then protected, then private.

  1.  **Import Statements** (handled by tools like 'Organize Imports').
  2.  **Angular Property Decorators:** @Input(), @Output(), @ViewChild(), etc.
  3.  **Class Properties/Fields.**
  4.  **Constructor.**
  5.  **Angular Lifecycle Hooks** (ngOnInit, ngOnDestroy, etc.).
  6.  **Methods.**

## 4\. Import Statements

Manage your imports for clarity and consistency.

- **Import Organization:** Use 'Organize Imports' in VS Code (or your preferred IDE) to automatically sort and clean up imports.
- **Multi-line Imports:** If a single import line becomes too long, split it into multiple lines for readability.
- **Specific Imports:** Avoid using \* (wildcard) to import all exports from a module. Explicitly list each function, class, or enum.
- **Relative Paths:** Use relative paths for local imports (e.g., ../services/my-service).

## 5\. Type Safety & Naming Nuances

Guidelines for robust typing and specific naming patterns.

- **Avoid any:** Minimize the use of the any type. Strive to use specific types whenever possible for better type safety and code understanding.
- **Event Naming:** Do not prefix output properties with on. Events should be named descriptively (e.g., userSelected, itemChanged).
- **Method Return Types:** Always explicitly declare the return type for your methods, except for constructors, Angular lifecycle hooks, and void methods.
- **Alphabetical Order:** Do not enforce alphabetical ordering for class members, properties, or methods unless explicitly desired for specific sections.
- **Variable/Function Naming:** Use **camelCase** for all variable and function names.
- **Private Member Prefix:** Prefix private data members with an underscore \_ (e.g., private \_userName: string;).
- **Observable Suffix:** Suffix Observable properties with a dollar sign $ (e.g., userData$: Observable;).
- **Conventional Suffixes:** Always use the conventional suffix for file types (e.g., .directive.ts, .module.ts, .pipe.ts, .service.ts).
- **Model Suffix:** Do not use a conventional suffix for model files (e.g., user.ts instead of user.model.ts).

## 6\. HTML Templating

Craft clean and efficient HTML templates.

- **Logic in Templates:** Avoid complex business logic within templates. Delegate all significant computations and data transformations to TypeScript functions or pipes.
- **Class Binding Preference:** Prefer \[class.your-classname\]="expression" for conditional class application over \[ngClass\]="{ 'your-classname': expression }".

## 7\. Pendo Integration

Guidelines for Pendo tagging.

- **New UI Elements:** New UI elements should generally include Pendo tags.
- **Pendo Verbiage:** Refer to the corresponding Jira card for the exact Pendo verbiage required.

## 8\. General Coding Conventions

Common coding style rules.

- **Indentation:** Use **2 spaces** for indentation.
- **End of File:** Add one extra line at the end of each file (TSLint default).
- **Function Arguments:** If a function or method has more than three arguments, place each argument on a new line. For three or fewer arguments, a single line is acceptable, considering overall line length.

## 9\. Refactoring & Cleanup Notes

Ongoing improvements for code hygiene.

- **Filename Kebab-Case:** Fix any file names that do not adhere to kebab-case using appropriate refactoring tools (e.g., TFS rename).

  - **Bad:** tenantVoucher.ts
  - **Good:** tenant-voucher.ts

- **Nested Folder Depth:** Consider flattening deeply nested file structures to improve navigability.
- **Folder Naming Repetition:** Avoid repeating the parent folder name in sub-folders (e.g., certification/certification-hud50058 should be certification/hud50058).

By embracing these standards, our Angular projects will be more consistent, robust, and a pleasure to develop and maintain collaboratively.
