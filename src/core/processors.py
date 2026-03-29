import re


def chunk_diffs(files):
    chunks = []

    for file in files:
        filename = file["filename"]
        patch = file["patch"]
        if not patch:
            continue

        # Find all hunk headers
        hunk_headers = list(re.finditer(r"@@ -\d+,\d+ \+(\d+),\d+ @@", patch))
        hunk_positions = [m.start() for m in hunk_headers]

        hunk_texts = []
        for i in range(len(hunk_positions)):
            start = hunk_positions[i]
            end = hunk_positions[i + 1] if i + 1 < len(hunk_positions) else len(patch)
            hunk_texts.append(patch[start:end])

        for hunk in hunk_texts:
            header_match = re.search(r"\+(\d+)", hunk)
            if not header_match:
                continue

            current_new_line = int(header_match.group(1))
            lines_with_numbers = []
            has_added_line = False

            for line in hunk.splitlines():
                if line.startswith("@@"):
                    continue

                if line.startswith("+"):
                    has_added_line = True
                    lines_with_numbers.append(
                        {"ln": current_new_line, "type": "added", "content": line[1:]}
                    )
                    current_new_line += 1

                elif line.startswith(" "):
                    lines_with_numbers.append(
                        {"ln": current_new_line, "type": "context", "content": line[1:]}
                    )
                    current_new_line += 1

                elif line.startswith("-"):
                    continue

            # Only keep chunks that contain actual changes
            if has_added_line:
                chunks.append({"file": filename, "lines": lines_with_numbers})

    return chunks
