# C# Development Standards: A Guide to Clean Code

This document establishes a set of coding standards for C# projects, promoting consistency, readability, and maintainability across our codebase. Adherence to these principles enhances collaboration and reduces the likelihood of issues.

## 1\. Core Principles: The SOLID Foundation

We champion the **SOLID principles** as the bedrock of our C# development:

- **Single Responsibility Principle (SRP):** Each class should have one, and only one, reason to change. It should do one job well.
- **Open/Closed Principle (OCP):** Software entities (classes, modules, functions, etc.) should be open for extension but closed for modification.
- **Liskov Substitution Principle (LSP):** Derived classes must be completely substitutable for their base classes without altering correctness.
- **Interface Segregation Principle (ISP):** Create granular, client-specific interfaces rather than monolithic ones.
- **Dependency Inversion Principle (DIP):** Depend on abstractions, not on concrete implementations.

## 2\. Overall Clean Code Practices

Beyond SOLID, these practices ensure clarity and efficiency:

- **Expressive Naming:**

  - A class or method's behavior should be immediately evident from its name. Avoid surprises.
  - Don't use abbreviations unless they are widely recognized industry standards (e.g., HUD, RFTA, USDA, HAP).
  - Embrace longer, more descriptive names when clarity is gained, even if it feels verbose at first.
  - _Example:_ Prefer CalculateMonthlyInterest() over CalcInt().

- **Method Argument Management:**

  - **Code Smell:** Methods accepting more than three arguments are often a sign of poor design.
  - **Solution:** Consider grouping related parameters into a dedicated data structure (class or struct) and passing that as a single argument. If parameters aren't closely related, refactor the method into smaller, more focused methods requiring fewer arguments.

- **Code Conciseness:** Keep classes compact and methods even more so. Break down large files into smaller, more manageable units when logical.
- **Line Length:** Ensure all code lines fit comfortably on a standard monitor without horizontal scrolling.
- **Unit Testing Imperative:**

  - **Always write unit tests** for your code. Untested code is considered unclean.
  - If a piece of code proves difficult to test, seek guidance from senior developers or initiate a team discussion. Such situations are valuable learning opportunities for new testing techniques.

- **Comments & Regions: Use Sparingly:**

  - **Comments:** Your code should strive to be self-documenting. If a comment is needed to clarify a method or class, consider renaming or restructuring the code to make its purpose obvious to the reader.
  - **Regions:** Avoid using #region directives. Hiding code within regions often indicates overly long or poorly structured code. All important code should be visible.

- **Variable Declarations:** All member/instance variable declarations should be consolidated at the top of their containing class.
- **Whitespace Intent:**

  - Avoid excessive vertical whitespace (more than one blank line between lines of code or methods).
  - Use single blank lines within methods to logically separate ideas or blocks of code.
  - **Consistency is paramount.** Inconsistent vertical whitespace makes code harder to scan and can mislead readers about code structure.

- **Fields vs. Properties:** Expose class state through **properties** rather than public fields.

  - Fields cannot be used in interfaces, hindering mockability in unit tests.
  - Properties facilitate adding validation logic (get/set) without breaking changes for consumers.
  - Direct field exposure violates the OOP principle of encapsulation, allowing any consumer to modify data directly.

- **Magic Numbers/Strings:** Never hardcode numeric or string literal values that are not intended for direct user display. Instead, declare them as named constants or enumerations for clarity and easy modification.
- **Formatting:** Utilize an editor.config file to enforce consistent code formatting across the project.
- **Dependency Scoping:** Do not inject Scoped or Transient lifetime services into a Singleton service. Similarly, avoid injecting Transient services into a Scoped service.

## 3\. File Naming & Project Organization

- **Single Class Per File:** Each source file should contain exactly one class or interface, and its name should match the class name (e.g., Lease.cs for the Lease class).
- **Descriptive Naming:** Use **PascalCase** and highly descriptive names for files. Avoid abbreviations unless they are widely understood.
- **Acronym Handling:**

  - For acronyms longer than two characters, use PascalCase (e.g., HtmlButton instead of HTMLButton).
  - For two-character acronyms, capitalize both characters (e.g., System.IO not System.Io).
  - Capitalize "ID" within ID fields (e.g., PropertyID).

## 4\. Architectural Layers & Standards

### 4.1 Services (Business Layer)

- **Data Flow:** Handle data input and output using well-defined **Models** when interacting with Controllers.
- **Repository Access:** Reference individual **Repositories** via Dependency Injection as needed.
- **Transaction Management:** Group multiple repository calls under a single transaction using Transaction.InTransaction() (which takes a lambda function) to ensure atomicity.
- **Dependency Depth:** Keep the dependency tree depth for services at a maximum of **15**. (e.g., if Service A depends on B, and B depends on C, A has a depth of 2).

### 4.2 Repositories

- Detailed standards for Repositories are maintained on a separate page.

### 4.3 DTOs (Data Transfer Objects)

- **Purpose:** Plain Old C# Objects (POCOs) used for passing data between the UI and Controllers.
- **Modeling:** DTOs should closely mirror the UI or the specific process they serve.
- **Complexity vs. Duplication:** For complex screens, composite DTOs may be necessary. However, prefer creating separate, clear DTOs even if it leads to some code duplication, rather than maintaining an overly complex web of interconnected DTOs.
- **Field Naming:** DTO fields should use **PascalCase** and be descriptive, avoiding abbreviations.
- **Primary/Foreign Key Fields:** Follow the same naming guidance as for Domain Model PKs/FKs (see below).

### 4.4 Domain Models

- **Purpose:** POCOs used within the Service layer to abstract database table implementations and to encapsulate business logic.
- **In-Model Logic:** This standard is under review. If you find a scenario where including business logic directly within a Domain Model would be beneficial, bring it up for team discussion.
- **Object Graphs (Under Review):** The standard generally discourages parent/child object graphs (a model containing references to other models). This is under review. If necessary, service code should explicitly instantiate and populate separate "child" objects.
- **Naming:** Model and field names do not need to precisely match database names (e.g., RMBuildingID instead of RMBLDGID). Use meaningful, plain-English class and property names.

  - _Example:_ Instead of NOLATE in the database, use NumberOfLatePayments in the model.

- **Primary and Foreign Key Properties:**

  - Should not be nullable; 0 can signify an unspecified value.
  - If a database table has a primary key identity field, name the property simply ID.
  - Place ID properties as the first member of their class.
  - For compound or multiple keys, specify each key with a descriptive name (e.g., RMPropertyID, RMBuildingID, RMUnitID).
  - If a model property holds a foreign key ID, use a descriptive name of the referenced table with an "ID" suffix (e.g., WaitingListStatusGroupID).

### 4.5 Mappers

- **SafeRow Usage:** Always use SafeRow in methods that interact with Row objects.
- **Value Retrieval:**

  - Get\_\_\_() functions should return the default value for their data types (e.g., 0 for int, false for bool).
  - Use GetNullable\_\_\_() functions when a database column is nullable and null is an expected or valid value.

### 4.6 Controllers

- **Dependency Limit:** Controllers should not depend on more than **30 total objects**, including implied dependencies (e.g., if a Controller depends on Service A, and Service A depends on Service B, both A and B count towards the limit).

By embracing these standards, our C# projects will be more consistent, robust, and a pleasure to develop and maintain collaboratively.
