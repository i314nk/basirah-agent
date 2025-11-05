"""
Search engine for basīrah analysis history.
Provides powerful search and filtering capabilities.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from src.storage.database import get_db

logger = logging.getLogger(__name__)


class AnalysisSearchEngine:
    """
    Search and filter analysis history with multiple criteria.
    """

    def __init__(self):
        """Initialize search engine."""
        self.db = get_db()

    def search(
        self,
        ticker: Optional[str] = None,
        company_name: Optional[str] = None,
        analysis_types: Optional[List[str]] = None,
        decisions: Optional[List[str]] = None,
        convictions: Optional[List[str]] = None,
        sharia_statuses: Optional[List[str]] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        min_roic: Optional[float] = None,
        min_margin_of_safety: Optional[float] = None,
        max_cost: Optional[float] = None,
        tags: Optional[List[str]] = None,
        sort_by: str = "date",
        sort_order: str = "desc",
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search analyses with multiple filters.

        Args:
            ticker: Stock ticker (e.g., "AAPL")
            company_name: Company name (fuzzy search)
            analysis_types: List of types: ["quick", "deep_dive", "sharia"]
            decisions: List of decisions: ["BUY", "WATCH", "AVOID", etc.]
            convictions: ["HIGH", "MODERATE", "LOW"]
            sharia_statuses: ["COMPLIANT", "DOUBTFUL", "NON-COMPLIANT"]
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            min_roic: Minimum ROIC percentage
            min_margin_of_safety: Minimum MoS percentage
            max_cost: Maximum analysis cost
            tags: List of tag names
            sort_by: Field to sort by
            sort_order: "asc" or "desc"
            limit: Maximum results to return
            offset: Number of results to skip

        Returns:
            List of matching analyses
        """
        # Build WHERE clauses
        where_clauses = []
        params = []

        if ticker:
            where_clauses.append("ticker ILIKE %s")
            params.append(f"%{ticker}%")

        if company_name:
            where_clauses.append("company_name ILIKE %s")
            params.append(f"%{company_name}%")

        if analysis_types:
            placeholders = ','.join(['%s'] * len(analysis_types))
            where_clauses.append(f"analysis_type IN ({placeholders})")
            params.extend(analysis_types)

        if decisions:
            # Normalize decisions to lowercase
            decisions_lower = [d.lower() for d in decisions]
            placeholders = ','.join(['%s'] * len(decisions_lower))
            where_clauses.append(f"LOWER(decision) IN ({placeholders})")
            params.extend(decisions_lower)

        if convictions:
            placeholders = ','.join(['%s'] * len(convictions))
            where_clauses.append(f"conviction IN ({placeholders})")
            params.extend(convictions)

        if sharia_statuses:
            placeholders = ','.join(['%s'] * len(sharia_statuses))
            where_clauses.append(f"sharia_status IN ({placeholders})")
            params.extend(sharia_statuses)

        if date_from:
            where_clauses.append("analysis_date >= %s")
            params.append(date_from)

        if date_to:
            where_clauses.append("analysis_date <= %s")
            params.append(date_to)

        if min_roic is not None:
            where_clauses.append("roic >= %s")
            params.append(min_roic)

        if min_margin_of_safety is not None:
            where_clauses.append("margin_of_safety >= %s")
            params.append(min_margin_of_safety)

        if max_cost is not None:
            where_clauses.append("cost <= %s")
            params.append(max_cost)

        if tags:
            # Join with tags
            where_clauses.append("""
                id IN (
                    SELECT at.analysis_id
                    FROM analysis_tags at
                    JOIN tags t ON at.tag_id = t.id
                    WHERE t.name = ANY(%s)
                )
            """)
            params.append(tags)

        # Build query
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        # Sort mapping
        sort_map = {
            "date": "analysis_date",
            "ticker": "ticker",
            "cost": "cost",
            "roic": "roic",
            "margin_of_safety": "margin_of_safety",
            "decision": "decision"
        }
        sort_field = sort_map.get(sort_by, "analysis_date")
        sort_direction = "DESC" if sort_order.lower() == "desc" else "ASC"

        # Build final query
        query = f"""
        SELECT *
        FROM v_analysis_summary
        WHERE {where_sql}
        ORDER BY {sort_field} {sort_direction}
        """

        if limit:
            query += f" LIMIT {limit}"
        if offset:
            query += f" OFFSET {offset}"

        try:
            results = self.db.execute_query(query, tuple(params))
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def quick_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Quick search by ticker or company name.

        Args:
            query: Search query

        Returns:
            Matching analyses sorted by date
        """
        sql = """
        SELECT *
        FROM v_analysis_summary
        WHERE ticker ILIKE %s OR company_name ILIKE %s
        ORDER BY analysis_date DESC
        LIMIT 20
        """

        search_term = f"%{query}%"
        try:
            return self.db.execute_query(sql, (search_term, search_term))
        except Exception as e:
            logger.error(f"Quick search failed: {e}")
            return []

    def get_by_ticker(
        self,
        ticker: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get all analyses for a specific ticker.

        Args:
            ticker: Stock ticker
            limit: Maximum results

        Returns:
            List of analyses for ticker
        """
        query = """
        SELECT *
        FROM v_analysis_summary
        WHERE ticker = %s
        ORDER BY analysis_date DESC
        LIMIT %s
        """

        try:
            return self.db.execute_query(query, (ticker.upper(), limit))
        except Exception as e:
            logger.error(f"Get by ticker failed: {e}")
            return []

    def get_recent(
        self,
        days: int = 30,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get recent analyses.

        Args:
            days: Number of days back
            limit: Maximum results

        Returns:
            Recent analyses
        """
        date_from = (datetime.now() - timedelta(days=days)).date()

        query = """
        SELECT *
        FROM v_analysis_summary
        WHERE analysis_date >= %s
        ORDER BY analysis_date DESC
        LIMIT %s
        """

        try:
            return self.db.execute_query(query, (date_from, limit))
        except Exception as e:
            logger.error(f"Get recent failed: {e}")
            return []

    def get_portfolio_candidates(self) -> List[Dict[str, Any]]:
        """
        Get high-conviction BUY decisions.

        Returns:
            List of BUY analyses with HIGH conviction
        """
        query = """
        SELECT *
        FROM v_analysis_summary
        WHERE decision = 'buy'
          AND conviction = 'HIGH'
        ORDER BY margin_of_safety DESC
        """

        try:
            return self.db.execute_query(query)
        except Exception as e:
            logger.error(f"Get portfolio candidates failed: {e}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about analysis history.

        Returns:
            Statistics dictionary
        """
        stats_query = """
        SELECT
            COUNT(*) as total_analyses,
            COUNT(DISTINCT ticker) as unique_companies,
            SUM(cost) as total_cost,
            SUM(duration_seconds) / 3600.0 as total_time_hours,
            MIN(analysis_date) as first_analysis,
            MAX(analysis_date) as last_analysis,
            COUNT(*) FILTER (WHERE analysis_type = 'quick') as quick_screens,
            COUNT(*) FILTER (WHERE analysis_type = 'deep_dive') as deep_dives,
            COUNT(*) FILTER (WHERE analysis_type = 'sharia') as sharia_screens,
            COUNT(*) FILTER (WHERE decision = 'buy') as buy_count,
            COUNT(*) FILTER (WHERE decision = 'watch') as watch_count,
            COUNT(*) FILTER (WHERE decision = 'avoid') as avoid_count,
            COUNT(*) FILTER (WHERE decision = 'investigate') as investigate_count,
            COUNT(*) FILTER (WHERE decision = 'pass') as pass_count,
            COUNT(*) FILTER (WHERE sharia_status = 'COMPLIANT') as compliant_count,
            COUNT(*) FILTER (WHERE sharia_status = 'DOUBTFUL') as doubtful_count,
            COUNT(*) FILTER (WHERE sharia_status = 'NON-COMPLIANT') as non_compliant_count
        FROM analyses
        """

        try:
            result = self.db.execute_query(stats_query)

            if not result:
                return {}

            stats = dict(result[0])

            # Calculate averages
            if stats['total_analyses'] > 0:
                stats['avg_cost'] = round(stats['total_cost'] / stats['total_analyses'], 2)
            else:
                stats['avg_cost'] = 0

            return stats
        except Exception as e:
            logger.error(f"Get statistics failed: {e}")
            return {}

    def full_text_search(self, search_term: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search thesis content using full-text search.

        Args:
            search_term: Term to search for
            limit: Maximum results

        Returns:
            Matching analyses
        """
        query = """
        SELECT *
        FROM v_analysis_summary
        WHERE thesis_full ILIKE %s
        ORDER BY analysis_date DESC
        LIMIT %s
        """

        try:
            search_pattern = f"%{search_term}%"
            return self.db.execute_query(query, (search_pattern, limit))
        except Exception as e:
            logger.error(f"Full-text search failed: {e}")
            return []

    def get_companies(self) -> List[Dict[str, Any]]:
        """
        Get list of all analyzed companies.

        Returns:
            List of companies with stats (only companies with at least 1 analysis)
        """
        query = """
        SELECT
            ticker,
            company_name,
            sector,
            industry,
            total_analyses,
            first_analyzed,
            last_analyzed
        FROM companies
        WHERE total_analyses > 0
        ORDER BY total_analyses DESC, last_analyzed DESC
        """

        try:
            return self.db.execute_query(query)
        except Exception as e:
            logger.error(f"Get companies failed: {e}")
            return []

    def get_tags(self) -> List[Dict[str, Any]]:
        """
        Get all available tags.

        Returns:
            List of tags
        """
        query = """
        SELECT
            t.id,
            t.name,
            t.description,
            t.color,
            COUNT(at.analysis_id) as usage_count
        FROM tags t
        LEFT JOIN analysis_tags at ON t.id = at.tag_id
        GROUP BY t.id, t.name, t.description, t.color
        ORDER BY usage_count DESC, t.name
        """

        try:
            return self.db.execute_query(query)
        except Exception as e:
            logger.error(f"Get tags failed: {e}")
            return []


__all__ = ["AnalysisSearchEngine"]
