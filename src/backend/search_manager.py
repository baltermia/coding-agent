from ddgs import DDGS


class SearchManager:
    def perform_search(self, query: str) -> list[dict[str, str]]:
        if not query.strip():
            return []

        parsed: list[dict[str, str]] = []
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=6)
            for item in results:
                parsed.append(
                    {
                        "title": item.get("title", "Result"),
                        "snippet": item.get("body", ""),
                        "url": item.get("href", ""),
                    }
                )
        return parsed
