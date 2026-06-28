"""Yahoo Finance tool: free, no-API-key stock quote and history via yfinance."""
from typing import Any, Dict
import yfinance as yf
from tools.base_tool import BaseTool
from utils.validators import validate_ticker
from utils.exceptions import ToolExecutionError


class YahooFinanceTool(BaseTool):
    name = "yahoo_finance"
    description = (
        "Fetch current price, key statistics, and recent price history for a stock ticker, "
        "using Yahoo Finance (no API key required)."
    )

    def schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol, e.g. MSFT"},
                    "period": {
                        "type": "string",
                        "description": "History period, e.g. '5d', '1mo', '1y'.",
                        "default": "5d",
                    },
                },
                "required": ["ticker"],
            },
        }

    def _run(self, ticker: str, period: str = "5d") -> Dict[str, Any]:
        """
        Validate and normalize a stock ticker symbol.

        A ticker symbol is a unique short code assigned to a publicly traded
        company or financial asset on a stock exchange (e.g., AAPL for Apple,
        MSFT for Microsoft, TSLA for Tesla).

        Args:
            ticker: Stock ticker symbol provided by the user.

        Returns:
            The normalized ticker symbol in uppercase.

        Raises:
            ValidationError: If the ticker is empty or does not match
            the expected ticker format.
        """
        ticker = validate_ticker(ticker)
        try:
            stock = yf.Ticker(ticker)
            info = stock.info or {}
            hist = stock.history(period=period)
        except Exception as exc:  # noqa: BLE001
            raise ToolExecutionError(self.name, f"yfinance lookup failed: {exc}") from exc

        if not info or info.get("regularMarketPrice") is None and hist.empty:
            raise ToolExecutionError(self.name, f"No data found for ticker '{ticker}'.")

        history_points = [
            {"date": str(idx.date()), "close": round(float(row["Close"]), 2)}
            for idx, row in hist.iterrows()
        ] if not hist.empty else []

        return {
            "ticker": ticker,
            "shortName": info.get("shortName"),
            "currentPrice": info.get("currentPrice") or info.get("regularMarketPrice"),
            "currency": info.get("currency"),
            "marketCap": info.get("marketCap"),
            "trailingPE": info.get("trailingPE"),
            "forwardPE": info.get("forwardPE"),
            "dividendYield": info.get("dividendYield"),
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
            "history": history_points,
        }
