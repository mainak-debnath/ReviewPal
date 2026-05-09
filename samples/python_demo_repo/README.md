# Python Demo Repo

This sample codebase is intentionally small but realistic enough to exercise ReviewPal's retrieval and standards-aware review flow.

Suggested demo path:
1. index this repository with `repo_id` set to the demo repo
2. create a GitHub repository from this folder
3. open a PR with intentionally flawed changes
4. run ReviewPal against that PR

The code is organized around an order checkout workflow with pricing, inventory, payment, and persistence concerns spread across multiple modules so retrieval can provide useful context.
