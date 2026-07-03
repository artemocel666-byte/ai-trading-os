from app.core.exceptions import NotImplementedFeatureError


class AnalysisService:
    """Foundation boundary for future analysis.

    The service exists so adapters can explicitly refuse analysis in phase one without
    fabricating a scan result or producing a financial recommendation.
    """

    async def scan_now(self) -> None:
        raise NotImplementedFeatureError("analysis_engine")
