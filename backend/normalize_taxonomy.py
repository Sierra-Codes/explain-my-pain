# Utility script (optional): normalises raw taxonomy lists; not used at runtime path
import json
import sys


def main():
    data = json.load(open(sys.argv[1]))
    # example: lowercase all expressions
    for k, v in data.get("metaphor_types", {}).items():
        v["expressions"] = sorted(
            set([s.strip() for s in v.get("expressions", [])]), key=str.lower)
    json.dump(data, open(sys.argv[2], "w"), indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
