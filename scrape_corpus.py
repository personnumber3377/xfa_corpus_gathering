#!/usr/bin/env python3
import os
import re
import sys

def extract_xfa_sections(data: str) -> list[str]:
    """
    Extract all <xdp:xdp ...> ... </xdp:xdp> sections from PDF text content.
    Returns a list of XML strings.
    """
    # Regex to match <xdp:xdp ...> ... </xdp:xdp>
    # DOTALL = allow multiline, non-greedy for inner matches
    pattern = re.compile(r"<xdp:xdp\b.*?</xdp:xdp>", re.DOTALL | re.IGNORECASE)
    matches = pattern.findall(data)
    return matches


def process_file(filepath: str, outdir: str, counter: int) -> int:
    """Read file, extract XFA sections, and save each one to the output corpus dir."""
    try:
        with open(filepath, "rb") as f:
            raw = f.read()
    except Exception as e:
        print(f"[!] Failed to read {filepath}: {e}")
        return counter

    # Try decoding as UTF-8 or Latin-1 (PDF streams may contain mixed encodings)
    try:
        text = raw.decode("utf-8", errors="ignore")
    except UnicodeDecodeError:
        text = raw.decode("latin-1", errors="ignore")

    xfa_sections = extract_xfa_sections(text)
    if not xfa_sections:
        return counter

    for section in xfa_sections:
        # Clean up whitespace and maybe truncate huge files
        section = section.strip()
        if len(section) > 10_000_000:  # skip massive blobs
            print(f"[!] Skipping huge section in {filepath}")
            continue

        # Write to corpus file
        outpath = os.path.join(outdir, f"xfa_{counter:05d}.xfa")
        with open(outpath, "w", encoding="utf-8") as out:
            out.write(section)
        print(f"[+] Extracted XFA -> {outpath}")
        counter += 1

    return counter


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <input_dir> <output_corpus_dir>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)

    counter = 0
    for root, _, files in os.walk(input_dir):
        for name in files:
            # Accept both .pdf and text files
            if not name.lower().endswith((".pdf", ".txt", ".dat")):
                continue
            filepath = os.path.join(root, name)
            counter = process_file(filepath, output_dir, counter)

    print(f"\n[✓] Extraction complete. Saved {counter} XFA sections to {output_dir}")


if __name__ == "__main__":
    main()