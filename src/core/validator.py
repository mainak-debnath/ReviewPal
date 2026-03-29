def validate_comments(comments, chunks):
    """
    Validates comments to ensure:
    - Only added lines are commented
    - No duplicates
    - Valid format
    """

    valid = []
    seen = set()

    # Build lookup: { file → set(valid_added_lines) }
    valid_lines_map = {}

    for chunk in chunks:
        filename = chunk["file"]

        if filename not in valid_lines_map:
            valid_lines_map[filename] = set()

        for line_data in chunk["lines"]:
            if line_data["type"] == "added":
                valid_lines_map[filename].add(line_data["ln"])

    for c in comments:
        # --- Normalize ---
        body = str(c.get("body", "")).strip()

        try:
            line_num = int(c.get("line"))
        except:
            continue

        filename = c.get("path")

        # --- Basic checks ---
        if not body:
            continue

        if filename not in valid_lines_map:
            print(f"⚠️ Dropping: File {filename} not in PR.")
            continue

        # --- Core validation ---
        if line_num not in valid_lines_map[filename]:
            print(f"⚠️ Dropping: Line {line_num} in {filename} is not an added line.")
            continue

        # --- Deduplication ---
        key = (filename, line_num, body)
        if key in seen:
            continue

        seen.add(key)

        valid.append({"path": filename, "line": line_num, "body": body})

    return valid
