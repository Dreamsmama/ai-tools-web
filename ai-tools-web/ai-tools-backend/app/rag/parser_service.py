from __future__ import annotations

import json


class ParserService:
    def parse(self, file_bytes: bytes, mime_type: str, filename: str) -> str:
        if not file_bytes:
            return ""

        low_name = filename.lower()
        try:
            if "json" in mime_type or low_name.endswith(".json"):
                data = json.loads(file_bytes.decode("utf-8", errors="ignore"))
                return json.dumps(data, ensure_ascii=False, indent=2)
            return file_bytes.decode("utf-8", errors="ignore")
        except Exception:
            return file_bytes.decode("utf-8", errors="ignore")


parser_service = ParserService()
