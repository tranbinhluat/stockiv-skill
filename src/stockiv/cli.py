"""
StockIV CLI — entry points for AI skills to call via `uv run`.

Commands:
    stockiv-collect   Fetch financial + context data for a ticker or macro
    stockiv-report    Convert a markdown report to PDF
    stockiv-publish   Publish a report to Discord
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pyrootutils
from dotenv import load_dotenv

load_dotenv()

# ─── Paths ───────────────────────────────────────────────────────────────────

ROOT = pyrootutils.find_root(search_from=__file__, indicator=".env")
DATA_DIR = ROOT / "data"
RAW_CONTEXT_DIR = DATA_DIR / "raw" / "context"
RAW_CACHE_DIR = DATA_DIR / "raw" / "cache"
PROCESSED_SYNTHESIZER_DIR = DATA_DIR / "processed" / "synthesizer"
REPORT_TICKER_DIR = ROOT / "reports" / "ticker"

FRESHNESS_DAYS = 7  # skip re-fetch if data is newer than this


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _is_fresh(path: Path, days: int = FRESHNESS_DAYS) -> bool:
    """Return True if file exists and is newer than `days` days."""
    if not path.exists():
        return False
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    return datetime.now() - mtime < timedelta(days=days)


def _ensure_dirs(*dirs: Path) -> None:
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def _get_peers_for_ticker(ticker: str) -> list[str]:
    """Determine 1-2 top competitors for a given ticker."""
    peer_map = {
        "FPT": ["CMG", "CTR"],
        "MWG": ["FRT", "DGW"],
        "PNJ": ["MWG"],
        "HPG": ["HSG", "NKG"],
        "VHM": ["NLG", "KDH"],
        "NLG": ["KDH", "VHM"],
        "KDH": ["NLG", "VHM"],
        "VCB": ["BID", "CTG"],
        "TCB": ["MBB", "ACB"],
        "ACB": ["MBB", "TCB"],
        "MBB": ["TCB", "ACB"],
        "CTG": ["BID", "VCB"],
        "BID": ["CTG", "VCB"],
        "MSN": ["SAB"],
        "GAS": ["PLX"],
        "GMD": ["HAH"],
        "HAH": ["GMD"],
    }
    
    ticker_upper = ticker.upper()
    if ticker_upper in peer_map:
        return peer_map[ticker_upper]
        
    import sqlite3
    db_path = ROOT / "data" / "stockiv.db"
    if db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT industry FROM company_overview WHERE ticker = ?", (ticker_upper,))
            row = cursor.fetchone()
            if row and row[0]:
                industry = row[0]
                cursor.execute(
                    "SELECT ticker FROM company_overview WHERE industry = ? AND ticker != ? LIMIT 2",
                    (industry, ticker_upper)
                )
                peers = [r[0] for r in cursor.fetchall() if r[0]]
                conn.close()
                return peers
            conn.close()
        except Exception:
            pass
            
    return []


# ─── collect ─────────────────────────────────────────────────────────────────


def _collect_ticker(ticker: str, data_type: str, force: bool) -> None:
    """Fetch financial data and context for a single ticker."""
    ticker = ticker.upper()
    ticker_dir = PROCESSED_SYNTHESIZER_DIR / ticker
    _ensure_dirs(ticker_dir, RAW_CONTEXT_DIR)

    summary_path = ticker_dir / "financial_summary.md"
    context_path = RAW_CONTEXT_DIR / f"{ticker}_ticker_context.md"

    # ── Financials ────────────────────────────────────────────────────────────
    if data_type in ("financials", "all"):
        if not force and _is_fresh(summary_path):
            print(
                f"[collect] financial_summary.md is fresh (<{FRESHNESS_DAYS}d). Skipping. Use --force to re-fetch."
            )
        else:
            print(f"[collect] Fetching financials for {ticker}...")
            sys.path.insert(0, str(ROOT / "tools"))
            from vnstock_tools import (
                fetch_financial_statements,
                fetch_financial_ratios,
                fetch_ratio_summary,
                fetch_company_overview,
                fetch_dividend_history,
                crawl_vietstock_ratios,
                crawl_vnindex_ratios,
            )
            from sqlite_tools import fetch_current_market_snapshot

            sections: list[str] = []

            sections.append(
                f"# Financial Summary: {ticker}\n_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n"
            )

            for label, fn, args in [
                ("## Company Overview", fetch_company_overview, (ticker,)),
                ("## Financial Statements (5Y)", fetch_financial_statements, (ticker,)),
                ("## Financial Ratios", fetch_financial_ratios, (ticker,)),
                ("## Ratio Summary (GCCP Metrics)", fetch_ratio_summary, (ticker,)),
                ("## Dividend History", fetch_dividend_history, (ticker,)),
                ("## Vietstock Ratios", crawl_vietstock_ratios, (ticker,)),
                ("## Current Market Snapshot (VNINDEX)", crawl_vnindex_ratios, ()),
                (
                    "## Current Market Snapshot (Ticker)",
                    fetch_current_market_snapshot,
                    (ticker,),
                ),
            ]:
                print(f"  → {label.strip('# ')}")
                try:
                    result = fn(*args)
                    sections.append(f"{label}\n\n{result}\n")
                except Exception as e:
                    sections.append(f"{label}\n\n⚠️ Error: {e}\n")

            summary_path.write_text("\n---\n\n".join(sections), encoding="utf-8")
            print(f"[collect] ✅ Saved: {summary_path}")

            # ── Auto-Fetch Peer Financials ────────────────────────────────────
            peers = _get_peers_for_ticker(ticker)
            if peers:
                print(f"[collect] Auto-fetching financials for peers: {', '.join(peers)}")
                for peer in peers:
                    try:
                        # Fetch peer financials in background/sub-call (non-force to avoid rate limits)
                        _collect_ticker(peer, data_type="financials", force=False)
                    except Exception as e:
                        print(f"[collect] ⚠️ Failed to auto-fetch peer {peer}: {e}")

    # ── Context (news) ────────────────────────────────────────────────────────
    if data_type in ("context", "all"):
        if not force and _is_fresh(context_path):
            print(f"[collect] {ticker}_ticker_context.md is fresh. Skipping.")
        else:
            print(f"[collect] Fetching news context for {ticker}...")
            sys.path.insert(0, str(ROOT / "tools"))
            from brave_tools import search_market_context

            queries = [
                f"{ticker} Vietnam stock earnings revenue profit 2025",
                f"{ticker} Vietnam management governance news 2025",
                f"{ticker} Vietnam industry outlook macro 2025",
            ]
            context_parts = [
                f"# Ticker Context: {ticker}\n_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n"
            ]
            for q in queries:
                print(f"  → Searching: {q[:60]}...")
                try:
                    result = search_market_context(q, days_back=14)
                    context_parts.append(f"## Query: {q}\n\n{result}\n")
                except Exception as e:
                    context_parts.append(f"## Query: {q}\n\n⚠️ Error: {e}\n")

            context_path.write_text("\n---\n\n".join(context_parts), encoding="utf-8")
            print(f"[collect] ✅ Saved: {context_path}")

    # ── Annual Report ─────────────────────────────────────────────────────────
    if data_type in ("annual-report", "all"):
        print(f"[collect] Checking annual report for {ticker}...")
        sys.path.insert(0, str(ROOT / "tools"))
        from report_finder_tools import search_annual_report_pdf, download_and_convert_pdf
        import json

        current_year = str(datetime.now().year)
        try:
            search_res = search_annual_report_pdf(ticker, current_year)
            urls = json.loads(search_res)
            if urls and len(urls) > 0:
                # Find first pdf/zip URL
                target_url = None
                for item in urls:
                    url = item.get("url", "")
                    if any(url.lower().endswith(ext) for ext in [".pdf", ".zip"]) or "Baocaothuongnien" in url:
                        target_url = url
                        break
                if not target_url:
                    target_url = urls[0].get("url", "")

                # Determine the target year from URL or fallback
                import re
                year_match = re.search(r"(20\d{2})", target_url)
                year = year_match.group(1) if year_match else str(int(current_year) - 1)

                md_dir = DATA_DIR / "processed" / "annual_reports" / ticker
                _ensure_dirs(md_dir)
                md_path = md_dir / f"{ticker}_annual_report_{year}.md"
                pdf_dir = DATA_DIR / "raw" / "annual_reports"

                if not force and md_path.exists():
                    print(f"[collect] Annual report markdown is fresh: {md_path}. Skipping.")
                else:
                    print(f"[collect] Downloading & converting annual report from {target_url}...")
                    res_dl = download_and_convert_pdf(target_url, ticker, str(md_path), str(pdf_dir))
                    print(f"[collect] {res_dl}")
            else:
                print(f"[collect] No annual report URLs found for {ticker}.")
                md_dir = DATA_DIR / "processed" / "annual_reports" / ticker
                _ensure_dirs(md_dir)
                (md_dir / "ANNUAL_REPORT_NOT_AVAILABLE").write_text("No annual report URL could be found.")
                print(f"[collect] Logged ANNUAL_REPORT_NOT_AVAILABLE for {ticker}")
        except Exception as e:
            print(f"[collect] ⚠️ Error collecting annual report: {e}")
            md_dir = DATA_DIR / "processed" / "annual_reports" / ticker
            _ensure_dirs(md_dir)
            (md_dir / "ANNUAL_REPORT_NOT_AVAILABLE").write_text(f"Error fetching annual report: {e}")


def _collect_macro(force: bool) -> None:
    """Fetch macro market context (VNINDEX + broad market news)."""
    _ensure_dirs(RAW_CONTEXT_DIR)
    macro_path = RAW_CONTEXT_DIR / "market_context.md"

    if not force and _is_fresh(macro_path):
        print(
            f"[collect] market_context.md is fresh (<{FRESHNESS_DAYS}d). Skipping. Use --force to re-fetch."
        )
        return

    print("[collect] Fetching macro market context...")
    sys.path.insert(0, str(ROOT / "tools"))
    from brave_tools import search_market_context
    from vnstock_tools import crawl_vnindex_ratios

    parts = [
        f"# Market Context\n_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n"
    ]

    # VNINDEX snapshot
    print("  → VNINDEX ratios...")
    try:
        vnindex = crawl_vnindex_ratios()
        parts.append(f"## VNINDEX Snapshot\n\n{vnindex}\n")
    except Exception as e:
        parts.append(f"## VNINDEX Snapshot\n\n⚠️ Error: {e}\n")

    # Macro news
    macro_queries = [
        "Vietnam stock market VNINDEX macro economic outlook 2025",
        "Vietnam GDP inflation interest rate Fed policy impact 2025",
        "Vietnam market sentiment investor foreign flow 2025",
    ]
    for q in macro_queries:
        print(f"  → Searching: {q[:60]}...")
        try:
            result = search_market_context(q, days_back=7)
            parts.append(f"## Query: {q}\n\n{result}\n")
        except Exception as e:
            parts.append(f"## Query: {q}\n\n⚠️ Error: {e}\n")

    macro_path.write_text("\n---\n\n".join(parts), encoding="utf-8")
    print(f"[collect] ✅ Saved: {macro_path}")


def collect(args: list[str] | None = None) -> None:
    """Entry point for `stockiv-collect`."""
    parser = argparse.ArgumentParser(
        prog="stockiv-collect",
        description="Fetch financial data and context for stock analysis.",
    )
    parser.add_argument("--ticker", type=str, help="Ticker symbol (e.g. FPT, MWG)")
    parser.add_argument(
        "--type",
        dest="data_type",
        choices=["financials", "context", "annual-report", "all"],
        default="all",
        help="Type of data to collect (default: all)",
    )
    parser.add_argument(
        "--macro",
        action="store_true",
        help="Collect macro market data instead of ticker-specific data",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=f"Re-fetch even if data is newer than {FRESHNESS_DAYS} days",
    )

    parsed = parser.parse_args(args)

    if parsed.macro:
        _collect_macro(force=parsed.force)
    elif parsed.ticker:
        _collect_ticker(parsed.ticker, parsed.data_type, force=parsed.force)
    else:
        parser.error("Provide --ticker TICKER or --macro")


# ─── report ──────────────────────────────────────────────────────────────────


def report(args: list[str] | None = None) -> None:
    """Entry point for `stockiv-report`. Converts a markdown report to PDF."""
    parser = argparse.ArgumentParser(
        prog="stockiv-report",
        description="Convert a GCCP markdown report to PDF.",
    )
    parser.add_argument(
        "--ticker", type=str, help="Ticker symbol — used to locate the report file"
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Explicit path to the markdown report file (overrides --ticker lookup)",
    )
    parser.add_argument(
        "--format",
        choices=["md", "pdf", "both"],
        default="pdf",
        help="Output format (default: pdf)",
    )
    parser.add_argument(
        "--financial-summary",
        type=str,
        default="",
        help="Optional path to financial_summary.md for appendix",
    )

    parsed = parser.parse_args(args)

    # Resolve input file
    if parsed.input:
        md_path = Path(parsed.input)
    elif parsed.ticker:
        ticker = parsed.ticker.upper()
        md_path = REPORT_TICKER_DIR / f"{ticker}_GCCP_report.md"
    else:
        parser.error("Provide --ticker TICKER or --input FILE")
        return

    if not md_path.exists():
        print(f"[report] ❌ Report file not found: {md_path}", file=sys.stderr)
        sys.exit(1)

    if parsed.format == "md":
        print(f"[report] ✅ Markdown already at: {md_path}")
        return

    # Convert to PDF
    sys.path.insert(0, str(ROOT / "tools"))
    from pdf_exporter_tool import markdown_to_pdf

    pdf_path = str(md_path.with_suffix(".pdf"))
    md_content = md_path.read_text(encoding="utf-8")

    financial_summary = parsed.financial_summary
    if not financial_summary and parsed.ticker:
        candidate = (
            PROCESSED_SYNTHESIZER_DIR / parsed.ticker.upper() / "financial_summary.md"
        )
        if candidate.exists():
            financial_summary = str(candidate)

    print(f"[report] Converting {md_path.name} → PDF...")
    result = markdown_to_pdf(md_content, pdf_path, financial_summary)
    print(f"[report] {result}")


# ─── publish ─────────────────────────────────────────────────────────────────


def publish(args: list[str] | None = None) -> None:
    """Entry point for `stockiv-publish`. Sends a report to Discord."""
    parser = argparse.ArgumentParser(
        prog="stockiv-publish",
        description="Publish a report markdown to Discord.",
    )
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="Path to the PDF report file to attach",
    )
    parser.add_argument(
        "--message",
        type=str,
        default="",
        help="Short summary post text to send to Discord (replaces sending the full file as text)",
    )
    parser.add_argument(
        "--channel",
        choices=["weekly", "ticker"],
        default="ticker",
        help="Target Discord channel type (default: ticker)",
    )
    parser.add_argument(
        "--attach-pdf",
        action="store_true",
        help="(Deprecated) PDF is now always attached when --file points to a .pdf",
    )

    parsed = parser.parse_args(args)

    file_path = Path(parsed.file)
    if not file_path.exists():
        print(f"[publish] ❌ File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Resolve Discord channel ID
    from stockiv.config.discord import get_discord_channel

    channel_map = {"weekly": "weekly_report", "ticker": "ticker_report"}
    try:
        channel_id = get_discord_channel(channel_map[parsed.channel])
    except ValueError as e:
        print(f"[publish] ❌ {e}", file=sys.stderr)
        sys.exit(1)

    # Determine post content — prefer explicit --message, fall back to file text
    if parsed.message:
        content = parsed.message
    elif file_path.suffix == ".md":
        content = file_path.read_text(encoding="utf-8")
    else:
        content = f"📎 Attached: `{file_path.name}`"

    # PDF attachment — use the file directly if it's a PDF, else look for a sibling
    pdf_path = None
    if file_path.suffix == ".pdf":
        pdf_path = str(file_path)
    else:
        candidate = file_path.with_suffix(".pdf")
        if candidate.exists():
            pdf_path = str(candidate)
        elif parsed.attach_pdf:
            print(f"[publish] ⚠️  PDF not found at {candidate}, sending text only.")

    sys.path.insert(0, str(ROOT / "tools"))
    from discord_publisher_tool import send_discord_message

    print(f"[publish] Sending to Discord channel {channel_id} ({parsed.channel})...")
    result = send_discord_message(channel_id, content, pdf_path)
    attached = f"+ PDF attached: {Path(pdf_path).name}" if pdf_path else "(no PDF)"
    print(f"[publish] {result} {attached}")
