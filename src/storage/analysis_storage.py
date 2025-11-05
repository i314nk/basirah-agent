"""
Analysis storage system for basīrah.
Stores analyses in both PostgreSQL (for search) and file system (for full content).
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from src.storage.database import get_db

logger = logging.getLogger(__name__)


class AnalysisStorage:
    """
    Manages storage of analysis results in both database and file system.

    Database: Stores metadata and enables fast search
    File System: Stores complete analysis JSON files
    """

    def __init__(self, storage_root: str = "basirah_analyses"):
        """
        Initialize storage system.

        Args:
            storage_root: Root directory for file storage
        """
        self.storage_root = Path(storage_root)
        self.db = get_db()
        self._ensure_directories()

    def _ensure_directories(self):
        """Create directory structure if it doesn't exist."""
        directories = [
            self.storage_root / "deep_dive" / "buy",
            self.storage_root / "deep_dive" / "watch",
            self.storage_root / "deep_dive" / "avoid",
            self.storage_root / "quick_screen" / "investigate",
            self.storage_root / "quick_screen" / "pass",
            self.storage_root / "sharia_screen" / "compliant",
            self.storage_root / "sharia_screen" / "doubtful",
            self.storage_root / "sharia_screen" / "non_compliant"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        logger.info(f"Storage directories ensured at {self.storage_root}")

    def save_analysis(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save analysis to both database and file system.

        Args:
            result: Analysis result from agent

        Returns:
            Storage metadata (paths, database ID, etc.)
        """
        try:
            # Extract key information
            ticker = result.get('ticker', 'UNKNOWN')

            # Determine analysis type
            analysis_type = self._determine_analysis_type(result)
            decision = result.get('decision', result.get('status', 'UNKNOWN'))
            analysis_date = datetime.now().date()

            # Normalize values
            analysis_type_normalized = self._normalize_analysis_type(analysis_type)
            decision_normalized = self._normalize_decision(decision, analysis_type_normalized)

            # Generate analysis ID
            years = result.get('metadata', {}).get('years_analyzed', 1)
            analysis_id = self._generate_analysis_id(
                ticker,
                analysis_date,
                decision_normalized,
                years if analysis_type_normalized == 'deep_dive' else None
            )

            # Determine file path
            file_path = self._get_file_path(
                analysis_type_normalized,
                decision_normalized,
                analysis_id
            )

            # Save to file system
            full_path = self.storage_root / file_path
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved analysis to file: {full_path}")

            # Save to database
            db_id = self._save_to_database(result, analysis_id, str(file_path), analysis_type_normalized)

            logger.info(f"Saved analysis to database with ID: {db_id}")

            return {
                "success": True,
                "analysis_id": analysis_id,
                "database_id": db_id,
                "file_path": str(full_path),
                "relative_path": str(file_path)
            }

        except Exception as e:
            logger.error(f"Failed to save analysis: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }

    def _determine_analysis_type(self, result: Dict[str, Any]) -> str:
        """Determine analysis type from result."""
        # Check if Sharia analysis
        if 'status' in result and result.get('status') in ['COMPLIANT', 'DOUBTFUL', 'NON-COMPLIANT']:
            return 'sharia'

        # Check metadata
        metadata = result.get('metadata', {})
        if 'analysis_type' in metadata:
            return metadata['analysis_type']

        # Check if has intrinsic value (deep dive)
        if result.get('intrinsic_value') is not None:
            return 'deep_dive'

        # Default to quick screen
        return 'quick'

    def _normalize_analysis_type(self, analysis_type: str) -> str:
        """Normalize analysis type to standard values."""
        type_map = {
            'quick': 'quick',
            'quick_screen': 'quick',
            'deep_dive': 'deep_dive',
            'deep': 'deep_dive',
            'sharia': 'sharia',
            'sharia_screen': 'sharia',
            'sharia_compliance': 'sharia'
        }
        return type_map.get(analysis_type.lower(), 'quick')

    def _normalize_decision(self, decision: str, analysis_type: str) -> str:
        """Normalize decision to lowercase for consistency."""
        decision_lower = decision.lower()

        # Map variations to standard values
        if analysis_type == 'sharia':
            if 'compliant' in decision_lower and 'non' not in decision_lower:
                return 'compliant'
            elif 'doubtful' in decision_lower:
                return 'doubtful'
            else:
                return 'non_compliant'
        elif analysis_type == 'quick':
            if 'investigate' in decision_lower:
                return 'investigate'
            else:
                return 'pass'
        else:  # deep_dive
            if 'buy' in decision_lower:
                return 'buy'
            elif 'watch' in decision_lower:
                return 'watch'
            else:
                return 'avoid'

    def _generate_analysis_id(
        self,
        ticker: str,
        date: datetime.date,
        decision: str,
        years: Optional[int] = None
    ) -> str:
        """Generate unique analysis ID."""
        base = f"{ticker}_{date.isoformat()}_{decision}"
        if years and years > 1:
            return f"{base}_{years}y"
        return base

    def _get_file_path(
        self,
        analysis_type: str,
        decision: str,
        analysis_id: str
    ) -> Path:
        """Determine file path based on analysis type and decision."""
        type_map = {
            'quick': 'quick_screen',
            'deep_dive': 'deep_dive',
            'sharia': 'sharia_screen'
        }

        dir_type = type_map.get(analysis_type, 'quick_screen')
        return Path(dir_type) / decision / f"{analysis_id}.json"

    def _save_to_database(
        self,
        result: Dict[str, Any],
        analysis_id: str,
        file_path: str,
        analysis_type: str
    ) -> int:
        """
        Save analysis metadata to database.

        Returns:
            Database ID of saved analysis
        """
        ticker = result.get('ticker', 'UNKNOWN')
        company_name = result.get('company_name', ticker)

        # Ensure company exists
        company_id = self._ensure_company_exists(ticker, company_name)

        # Extract metadata
        metadata = result.get('metadata', {})
        decision = result.get('decision', result.get('status', 'UNKNOWN'))
        decision_normalized = self._normalize_decision(decision, analysis_type)

        # Extract metrics
        conviction = result.get('conviction')
        intrinsic_value = result.get('intrinsic_value')
        current_price = result.get('current_price')
        margin_of_safety = result.get('margin_of_safety')

        # Extract financial metrics from metadata or result
        roic = None
        if 'roic' in result:
            roic = result['roic']
        elif 'financial_metrics' in metadata:
            roic = metadata['financial_metrics'].get('roic')

        # Sharia metrics
        sharia_status = result.get('status') if analysis_type == 'sharia' else None
        purification_rate = result.get('purification_rate', 0.0) if analysis_type == 'sharia' else None

        # Cost and performance
        token_usage = metadata.get('token_usage', {})
        cost = token_usage.get('total_cost', 0.0)
        duration = metadata.get('analysis_duration_seconds', 0)

        # Thesis content
        thesis = result.get('thesis', '') or result.get('analysis', '')
        thesis_preview = thesis[:500] if thesis else None

        # Insert into database
        query = """
        INSERT INTO analyses (
            analysis_id, company_id, ticker, company_name,
            analysis_type, analysis_date, analysis_datetime, years_analyzed,
            decision, conviction,
            intrinsic_value, current_price, margin_of_safety, roic,
            sharia_status, purification_rate,
            cost, duration_seconds,
            token_usage_input, token_usage_output,
            thesis_preview, thesis_full,
            file_path
        ) VALUES (
            %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s,
            %s, %s, %s, %s,
            %s, %s,
            %s, %s,
            %s, %s,
            %s, %s,
            %s
        ) RETURNING id
        """

        params = (
            analysis_id, company_id, ticker, company_name,
            analysis_type, datetime.now().date(), datetime.now(),
            metadata.get('years_analyzed'),
            decision_normalized, conviction,
            intrinsic_value, current_price, margin_of_safety, roic,
            sharia_status, purification_rate,
            cost, duration,
            token_usage.get('input_tokens'), token_usage.get('output_tokens'),
            thesis_preview, thesis,
            file_path
        )

        with self.db.get_cursor() as cur:
            cur.execute(query, params)
            db_id = cur.fetchone()['id']

        return db_id

    def _ensure_company_exists(self, ticker: str, company_name: str) -> int:
        """
        Ensure company exists in database, create if not.

        Returns:
            Company ID
        """
        # Try to find existing company
        query = "SELECT id FROM companies WHERE ticker = %s"
        result = self.db.execute_query(query, (ticker,))

        if result:
            return result[0]['id']

        # Create new company
        insert_query = """
        INSERT INTO companies (ticker, company_name)
        VALUES (%s, %s)
        RETURNING id
        """

        with self.db.get_cursor() as cur:
            cur.execute(insert_query, (ticker, company_name))
            company_id = cur.fetchone()['id']

        logger.info(f"Created new company: {ticker} (ID: {company_id})")
        return company_id

    def load_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Load complete analysis from file system.

        Args:
            analysis_id: Analysis ID

        Returns:
            Full analysis dictionary or None if not found
        """
        try:
            # Get file path from database
            query = "SELECT file_path FROM analyses WHERE analysis_id = %s"
            result = self.db.execute_query(query, (analysis_id,))

            if not result:
                logger.warning(f"Analysis not found: {analysis_id}")
                return None

            file_path = self.storage_root / result[0]['file_path']

            if not file_path.exists():
                logger.error(f"Analysis file not found: {file_path}")
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            logger.error(f"Failed to load analysis {analysis_id}: {e}")
            return None

    def delete_analysis(self, analysis_id: str) -> bool:
        """
        Delete analysis from both database and file system.

        Args:
            analysis_id: Analysis ID

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get file path
            query = "SELECT file_path FROM analyses WHERE analysis_id = %s"
            result = self.db.execute_query(query, (analysis_id,))

            if not result:
                logger.warning(f"Analysis not found: {analysis_id}")
                return False

            file_path = self.storage_root / result[0]['file_path']

            # Delete from database
            delete_query = "DELETE FROM analyses WHERE analysis_id = %s"
            self.db.execute_update(delete_query, (analysis_id,))

            # Delete file
            if file_path.exists():
                file_path.unlink()

            logger.info(f"Deleted analysis: {analysis_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete analysis {analysis_id}: {e}")
            return False

    def delete_company(self, ticker: str) -> Dict[str, Any]:
        """
        Delete a company and all its analyses from both database and file system.

        Args:
            ticker: Stock ticker (e.g., "AAPL")

        Returns:
            Dict with success status and count of deleted analyses
        """
        try:
            # Get all analyses for this company
            query = "SELECT analysis_id, file_path FROM analyses WHERE ticker = %s"
            analyses = self.db.execute_query(query, (ticker,))

            if not analyses:
                logger.warning(f"No analyses found for company: {ticker}")
                return {
                    'success': False,
                    'message': f'No analyses found for {ticker}',
                    'deleted_count': 0
                }

            deleted_count = 0
            failed_deletions = []

            # Delete each analysis
            for analysis in analyses:
                analysis_id = analysis['analysis_id']
                file_path = self.storage_root / analysis['file_path']

                try:
                    # Delete from database
                    delete_query = "DELETE FROM analyses WHERE analysis_id = %s"
                    self.db.execute_update(delete_query, (analysis_id,))

                    # Delete file
                    if file_path.exists():
                        file_path.unlink()

                    deleted_count += 1
                    logger.info(f"Deleted analysis: {analysis_id}")

                except Exception as e:
                    logger.error(f"Failed to delete analysis {analysis_id}: {e}")
                    failed_deletions.append(analysis_id)

            # Delete company record
            company_query = "DELETE FROM companies WHERE ticker = %s"
            self.db.execute_update(company_query, (ticker,))

            logger.info(f"Deleted company {ticker} and {deleted_count} analyses")

            return {
                'success': True,
                'message': f'Deleted {ticker} and {deleted_count} analyses',
                'deleted_count': deleted_count,
                'failed': failed_deletions
            }

        except Exception as e:
            logger.error(f"Failed to delete company {ticker}: {e}")
            return {
                'success': False,
                'message': f'Failed to delete {ticker}: {str(e)}',
                'deleted_count': 0
            }

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.

        Returns:
            Statistics about stored analyses
        """
        try:
            # Count files
            file_count = sum(1 for _ in self.storage_root.rglob('*.json'))

            # Calculate total size
            total_size = sum(f.stat().st_size for f in self.storage_root.rglob('*.json'))

            # Get database stats
            db_query = "SELECT COUNT(*) as count FROM analyses"
            db_result = self.db.execute_query(db_query)
            db_count = db_result[0]['count'] if db_result else 0

            return {
                "file_count": file_count,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "database_records": db_count,
                "storage_root": str(self.storage_root)
            }
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {}


__all__ = ["AnalysisStorage"]
