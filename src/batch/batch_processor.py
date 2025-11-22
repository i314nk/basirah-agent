"""
Batch processing engine for basīrah.

Handles automated screening of multiple companies following a protocol.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
import csv

from src.batch.protocols import BatchProtocol, AnalysisType, ProtocolStage
from src.agent.buffett_agent import WarrenBuffettAgent
from src.agent.sharia_screener import ShariaScreener
from src.storage import AnalysisStorage

logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    Processes multiple companies through a screening protocol.

    Handles progress tracking, error recovery, and stop/resume functionality.
    """

    def __init__(
        self,
        protocol: BatchProtocol,
        storage: AnalysisStorage,
        progress_callback: Optional[Callable] = None
    ):
        """
        Initialize batch processor.

        Args:
            protocol: Screening protocol to follow
            storage: Storage system for saving results
            progress_callback: Function to call with progress updates
        """
        self.protocol = protocol
        self.storage = storage
        self.progress_callback = progress_callback

        # Initialize agents
        self.buffett_agent = WarrenBuffettAgent()
        self.sharia_screener = ShariaScreener()

        # State tracking
        self.state = {
            "status": "idle",  # idle, running, paused, complete, error
            "batch_id": None,
            "start_time": None,
            "total_companies": 0,
            "current_stage": 0,
            "current_company_index": 0,
            "companies": [],
            "results": {},
            "errors": [],
            "stage_stats": []
        }

        self.should_stop = False

    def load_tickers_from_csv(self, csv_path: str) -> List[str]:
        """
        Load tickers from CSV file.

        Expected format:
        ticker
        AAPL
        MSFT
        ...

        Args:
            csv_path: Path to CSV file

        Returns:
            List of ticker symbols
        """
        tickers = []

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                if 'ticker' not in reader.fieldnames:
                    raise ValueError("CSV must have 'ticker' column")

                for row in reader:
                    ticker = row['ticker'].strip().upper()
                    if ticker and len(ticker) <= 5:  # Valid ticker format
                        tickers.append(ticker)

            # Remove duplicates while preserving order
            seen = set()
            unique_tickers = []
            for ticker in tickers:
                if ticker not in seen:
                    seen.add(ticker)
                    unique_tickers.append(ticker)

            logger.info(f"Loaded {len(unique_tickers)} tickers from {csv_path}")
            return unique_tickers

        except Exception as e:
            logger.error(f"Failed to load tickers from CSV: {e}")
            raise

    def start_batch(self, tickers: List[str], batch_id: Optional[str] = None, batch_name: Optional[str] = None) -> str:
        """
        Start batch processing.

        Args:
            tickers: List of ticker symbols to process
            batch_id: Optional batch ID (for resuming)
            batch_name: Optional custom batch name

        Returns:
            Batch ID
        """
        if not batch_id:
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Use custom name or generate from timestamp
        if not batch_name or not batch_name.strip():
            batch_name = f"Batch {datetime.now().strftime('%b %d, %Y %H:%M')}"

        self.state = {
            "status": "running",
            "batch_id": batch_id,
            "batch_name": batch_name,
            "start_time": datetime.now(),
            "total_companies": len(tickers),
            "current_stage": 0,
            "current_company_index": 0,
            "companies": tickers,
            "results": {ticker: {} for ticker in tickers},
            "errors": [],
            "stage_stats": []
        }

        self.should_stop = False

        logger.info(f"Starting batch '{batch_name}' ({batch_id}) with {len(tickers)} companies")
        self._send_progress()

        return batch_id

    def process_batch(self) -> Dict[str, Any]:
        """
        Process entire batch following protocol.

        Returns:
            Final batch results
        """
        try:
            # Process each stage
            for stage_index in range(self.protocol.total_stages()):
                if self.should_stop:
                    self.state["status"] = "paused"
                    logger.info(f"Batch paused at stage {stage_index}")
                    return self.state

                self.state["current_stage"] = stage_index
                self._process_stage(stage_index)

            # Batch complete
            self.state["status"] = "complete"
            self.state["end_time"] = datetime.now()

            duration = (self.state["end_time"] - self.state["start_time"]).total_seconds()
            self.state["duration_seconds"] = duration

            logger.info(f"Batch {self.state['batch_id']} complete in {duration:.0f}s")
            self._send_progress()

            # Save batch summary to database
            try:
                summary = self.get_summary()
                summary['protocol_description'] = self.protocol.description
                self.storage.save_batch(summary)
                logger.info(f"Saved batch summary to database: {self.state['batch_id']}")
            except Exception as e:
                logger.error(f"Failed to save batch summary: {e}")

            return self.state

        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            self.state["status"] = "error"
            self.state["error"] = str(e)
            return self.state

    def _process_stage(self, stage_index: int):
        """Process single stage of protocol."""
        stage = self.protocol.get_stage(stage_index)
        if not stage:
            return

        logger.info(f"Processing stage {stage_index + 1}/{self.protocol.total_stages()}: {stage.name}")

        # Get companies that should be processed in this stage
        companies_to_process = self._get_companies_for_stage(stage_index)

        stage_stats = {
            "stage_name": stage.name,
            "stage_index": stage_index,
            "companies_processed": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "start_time": datetime.now()
        }

        # Process each company
        for i, ticker in enumerate(companies_to_process):
            if self.should_stop:
                break

            self.state["current_company_index"] = i
            self._send_progress()

            try:
                # Run analysis
                result = self._run_analysis(ticker, stage)

                # Store result
                if ticker not in self.state["results"]:
                    self.state["results"][ticker] = {}

                self.state["results"][ticker][f"stage_{stage_index}"] = result

                # Save to database
                self.storage.save_analysis(result)

                # Track stats
                stage_stats["companies_processed"] += 1

                if stage.should_progress(result.get('decision', '')):
                    stage_stats["passed"] += 1
                else:
                    stage_stats["failed"] += 1

                logger.info(f"Completed {ticker}: {result.get('decision')}")

            except Exception as e:
                logger.error(f"Error processing {ticker} in stage {stage_index}: {e}")
                stage_stats["errors"] += 1
                self.state["errors"].append({
                    "ticker": ticker,
                    "stage": stage_index,
                    "error": str(e)
                })

        # Finalize stage stats
        stage_stats["end_time"] = datetime.now()
        stage_stats["duration_seconds"] = (
            stage_stats["end_time"] - stage_stats["start_time"]
        ).total_seconds()

        self.state["stage_stats"].append(stage_stats)

    def _get_companies_for_stage(self, stage_index: int) -> List[str]:
        """
        Get list of companies that should be processed in this stage.

        For stage 0, all companies.
        For stage N, only companies that passed stage N-1.
        """
        if stage_index == 0:
            return self.state["companies"]

        # Get previous stage
        prev_stage = self.protocol.get_stage(stage_index - 1)
        if not prev_stage:
            return []

        # Filter companies that passed previous stage
        companies = []
        for ticker in self.state["companies"]:
            prev_result = self.state["results"].get(ticker, {}).get(f"stage_{stage_index - 1}")
            if prev_result and prev_stage.should_progress(prev_result.get('decision', '')):
                companies.append(ticker)

        return companies

    def _run_analysis(self, ticker: str, stage: ProtocolStage) -> Dict[str, Any]:
        """Run analysis for a ticker at a specific stage."""

        if stage.analysis_type == AnalysisType.SHARIA:
            # Sharia screening
            result = self.sharia_screener.screen_company(ticker)

        elif stage.analysis_type == AnalysisType.QUICK:
            # Quick screen
            result = self.buffett_agent.analyze_company(
                ticker=ticker,
                deep_dive=False,
                years_to_analyze=1
            )

        elif stage.analysis_type == AnalysisType.DEEP_DIVE:
            # Deep dive
            years = stage.years_to_analyze or 5
            result = self.buffett_agent.analyze_company(
                ticker=ticker,
                deep_dive=True,
                years_to_analyze=years
            )

        else:
            raise ValueError(f"Unknown analysis type: {stage.analysis_type}")

        # Add batch metadata
        if 'metadata' not in result:
            result['metadata'] = {}

        result["metadata"]["batch_id"] = self.state["batch_id"]
        result["metadata"]["batch_stage"] = stage.name
        result["metadata"]["batch_stage_index"] = self.state["current_stage"]

        return result

    def _send_progress(self):
        """Send progress update via callback."""
        if self.progress_callback:
            try:
                self.progress_callback(self.state)
            except Exception as e:
                logger.error(f"Progress callback failed: {e}")

    def stop(self):
        """Stop batch processing (will finish current company)."""
        logger.info("Stop requested")
        self.should_stop = True

    def resume(self):
        """Resume paused batch processing."""
        if self.state["status"] == "paused":
            logger.info(f"Resuming batch {self.state['batch_id']}")
            self.should_stop = False
            self.state["status"] = "running"
            return self.process_batch()
        else:
            logger.warning("Cannot resume - batch not paused")
            return self.state

    def get_summary(self) -> Dict[str, Any]:
        """
        Generate summary report of batch results.

        Returns:
            Summary dictionary
        """
        summary = {
            "batch_id": self.state["batch_id"],
            "batch_name": self.state.get("batch_name", self.state["batch_id"]),
            "protocol": self.protocol.name,
            "status": self.state["status"],
            "total_companies": self.state["total_companies"],
            "start_time": self.state["start_time"],
            "end_time": self.state.get("end_time"),
            "duration_seconds": self.state.get("duration_seconds"),
            "stages": []
        }

        # Stage summaries
        for stage_stat in self.state["stage_stats"]:
            stage_summary = {
                "name": stage_stat["stage_name"],
                "companies_processed": stage_stat["companies_processed"],
                "passed": stage_stat["passed"],
                "failed": stage_stat["failed"],
                "errors": stage_stat["errors"],
                "duration_seconds": stage_stat["duration_seconds"]
            }
            summary["stages"].append(stage_summary)

        # Find top recommendations (BUY decisions from final stage)
        final_stage_index = self.protocol.total_stages() - 1
        buy_decisions = []

        for ticker, results in self.state["results"].items():
            final_result = results.get(f"stage_{final_stage_index}")
            if final_result and final_result.get('decision', '').lower() == 'buy':
                buy_decisions.append({
                    "ticker": ticker,
                    "decision": final_result.get('decision'),
                    "conviction": final_result.get('conviction'),
                    "analysis": final_result
                })

        summary["top_recommendations"] = buy_decisions

        # Calculate total cost
        total_cost = 0
        for results in self.state["results"].values():
            for stage_result in results.values():
                cost = stage_result.get('metadata', {}).get('token_usage', {}).get('total_cost', 0)
                total_cost += cost

        summary["total_cost"] = round(total_cost, 2)

        return summary


__all__ = ["BatchProcessor"]
