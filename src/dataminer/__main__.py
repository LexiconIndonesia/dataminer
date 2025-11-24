"""Main entry point for running the application."""

import uvicorn

from dataminer.core.config import get_settings


def main() -> None:
    """Run the application with uvicorn."""
    settings = get_settings()

    uvicorn.run(
        "dataminer.api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
