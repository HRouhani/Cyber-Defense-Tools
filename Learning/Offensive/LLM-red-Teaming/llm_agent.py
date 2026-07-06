#!/usr/bin/env python3
"""
Simple LangGraph + Ollama agent from OffSec Module 3.

Workflow:
1. Fetch stock sentiment data.
2. Select the most bullish stock.
3. Fetch its price.
4. Ask a local Ollama model to summarize the result.

Requirements:
    pip install requests langgraph langchain-ollama

Ollama model:
    ollama pull llama3.2:1b

Note:
The MegaCorp One API endpoints used below may only be reachable from
the corresponding OffSec lab environment.
"""

from __future__ import annotations

from typing import Any

import requests
from langchain_ollama import OllamaLLM
from langgraph.graph import END, StateGraph


MEGACORPONE_PROMPT = """
You are MegaCorp One AI, an expert stock-market analysis assistant.

Analyze the supplied stock-market sentiment and price data.
Explain why the stock may be receiving attention.

Do not provide direct investment recommendations.
Do not present the analysis as financial advice.
""".strip()


llm = OllamaLLM(
    model="llama3.2:1b",
)


def fetch_stock_data(state: dict[str, Any]) -> dict[str, Any]:
    """Retrieve stock sentiment data from the MegaCorp One Trades API."""

    url = (
        "https://trades.megacorpone.com/"
        "api/v1/apps/reddit?date=2024-04-05"
    )

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as error:
        return {
            **state,
            "error": f"Failed to fetch stock data: {error}",
        }
    except ValueError as error:
        return {
            **state,
            "error": f"Stock API returned invalid JSON: {error}",
        }

    if isinstance(data, dict):
        data = [data]

    if not isinstance(data, list) or not data:
        return {
            **state,
            "error": "No stock data found in the API response.",
        }

    return {
        **state,
        "stocks": data,
    }


def select_top_stock(state: dict[str, Any]) -> dict[str, Any]:
    """Select the bullish stock with the best sentiment and comment count."""

    if state.get("error"):
        return state

    stocks = state.get("stocks", [])

    bullish_stocks = [
        stock
        for stock in stocks
        if str(stock.get("sentiment", "")).lower() == "bullish"
    ]

    if not bullish_stocks:
        return {
            **state,
            "error": "No bullish stocks were found.",
        }

    try:
        top_stock = sorted(
            bullish_stocks,
            key=lambda stock: (
                -float(stock["sentiment_score"]),
                -int(stock["no_of_comments"]),
            ),
        )[0]
    except (KeyError, TypeError, ValueError) as error:
        return {
            **state,
            "error": f"Unexpected stock-data structure: {error}",
        }

    print(
        "\nSelected Most Bullish Stock: "
        f"{top_stock['ticker']} "
        f"(Sentiment Score: {top_stock['sentiment_score']}, "
        f"Comments: {top_stock['no_of_comments']})"
    )

    return {
        **state,
        "top_stock": top_stock,
    }


def fetch_stock_price(state: dict[str, Any]) -> dict[str, Any]:
    """Retrieve the stock price for the selected ticker."""

    if state.get("error"):
        return state

    top_stock = state.get("top_stock", {})
    ticker = top_stock.get("ticker")

    if not ticker:
        return {
            **state,
            "error": "No valid ticker was selected.",
        }

    print(f"Fetching stock price for: {ticker}")

    url = (
        "https://trades.megacorpone.com/"
        f"api/v1/price?ticker={ticker}&date=2024-04-05"
    )

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        response_data = response.json()
        stock_price = float(response_data["price"])
    except requests.RequestException as error:
        return {
            **state,
            "error": f"Failed to fetch stock price: {error}",
        }
    except (ValueError, KeyError, TypeError) as error:
        return {
            **state,
            "error": f"Unexpected stock-price response: {error}",
        }

    print(f"Stock Price for {ticker}: ${stock_price:.2f}")

    return {
        **state,
        "stock_price": {
            ticker: stock_price,
        },
    }


def generate_summary(state: dict[str, Any]) -> dict[str, Any]:
    """Use the local Ollama model to summarize the collected information."""

    if state.get("error"):
        print(f"\nError: {state['error']}")
        return state

    stock = state.get("top_stock", {})
    ticker = stock.get("ticker")
    prices = state.get("stock_price", {})
    price = prices.get(ticker)

    if not ticker or price is None:
        return {
            **state,
            "error": "Missing stock or price data.",
        }

    stock_details = f"""
{MEGACORPONE_PROMPT}

Stock data:

- Ticker: {ticker}
- Number of comments: {stock['no_of_comments']}
- Sentiment: {stock['sentiment']}
- Sentiment score: {stock['sentiment_score']}
- Current stock price: ${price:.2f}

Provide a concise analysis of why this stock may be trending.
""".strip()

    try:
        summary = llm.invoke(stock_details)
    except Exception as error:
        return {
            **state,
            "error": f"Ollama request failed: {error}",
        }

    print("\nMegaCorp One AI Summary:\n")
    print(summary.strip())
    print("\n" + "=" * 50 + "\n")

    return {
        **state,
        "summary": summary,
    }


def build_workflow():
    """Create and compile the LangGraph workflow."""

    workflow = StateGraph(dict)

    workflow.add_node(
        "fetch_stock_data",
        fetch_stock_data,
    )
    workflow.add_node(
        "select_top_stock",
        select_top_stock,
    )
    workflow.add_node(
        "fetch_stock_price",
        fetch_stock_price,
    )
    workflow.add_node(
        "generate_summary",
        generate_summary,
    )

    workflow.set_entry_point("fetch_stock_data")

    workflow.add_edge(
        "fetch_stock_data",
        "select_top_stock",
    )
    workflow.add_edge(
        "select_top_stock",
        "fetch_stock_price",
    )
    workflow.add_edge(
        "fetch_stock_price",
        "generate_summary",
    )
    workflow.add_edge(
        "generate_summary",
        END,
    )

    return workflow.compile()


def main() -> None:
    app = build_workflow()
    final_state = app.invoke({})

    if final_state.get("error"):
        raise SystemExit(final_state["error"])


if __name__ == "__main__":
    main()
