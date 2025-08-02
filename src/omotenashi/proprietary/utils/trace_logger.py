"""
Agent Trace Logging System
Captures every BDI decision for analysis and learning
"""
import asyncio
import aiosqlite
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json
import os


@dataclass
class DecisionPoint:
    """Represents a single decision point in agent processing"""
    timestamp: datetime
    decision_type: str  # 'belief_update', 'desire_prioritization', 'tool_selection', etc.
    beliefs_activated: Dict[str, Any]
    desires_prioritized: List[Dict[str, float]]
    tools_considered: List[Dict[str, Any]]
    tool_selected: Optional[str]
    reasoning_chain: List[str]
    pattern_id: Optional[str]
    outcome_expected: Dict[str, Any]
    confidence_scores: Dict[str, float]
    context: Dict[str, Any]


@dataclass
class TraceSession:
    """Represents a complete interaction session"""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime]
    decision_points: List[DecisionPoint]
    final_outcome: Optional[Dict[str, Any]]
    satisfaction_score: Optional[float]


class AgentTraceLogger:
    """Logs agent decision traces for analysis and learning"""
    
    def __init__(self, db_path: str = "logs/agent_traces.db"):
        self.db_path = db_path
        self.current_sessions: Dict[str, TraceSession] = {}
        self._ensure_db_directory()
        
    def _ensure_db_directory(self):
        """Ensure the database directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
    async def initialize_db(self):
        """Initialize database schema"""
        async with aiosqlite.connect(self.db_path) as db:
            # Main trace table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS decision_traces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    decision_type TEXT NOT NULL,
                    beliefs_json TEXT,
                    desires_json TEXT,
                    tools_json TEXT,
                    tool_selected TEXT,
                    reasoning_json TEXT,
                    pattern_id TEXT,
                    expected_outcome_json TEXT,
                    confidence_json TEXT,
                    context_json TEXT,
                    INDEX idx_session_id (session_id),
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_pattern_id (pattern_id)
                )
            """)
            
            # Session summary table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS trace_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    decision_count INTEGER DEFAULT 0,
                    final_outcome_json TEXT,
                    satisfaction_score REAL,
                    flagship_scenario TEXT,
                    INDEX idx_user_id (user_id),
                    INDEX idx_start_time (start_time)
                )
            """)
            
            # Pattern effectiveness table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS pattern_effectiveness (
                    pattern_id TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    avg_confidence REAL DEFAULT 0.0,
                    avg_satisfaction REAL DEFAULT 0.0,
                    last_used TEXT,
                    PRIMARY KEY (pattern_id)
                )
            """)
            
            # Tool selection patterns table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tool_selection_patterns (
                    intention TEXT NOT NULL,
                    belief_state_hash TEXT NOT NULL,
                    tool_selected TEXT NOT NULL,
                    selection_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0,
                    avg_confidence REAL DEFAULT 0.0,
                    PRIMARY KEY (intention, belief_state_hash, tool_selected)
                )
            """)
            
            await db.commit()
    
    async def start_session(self, session_id: str, user_id: str, 
                          flagship_scenario: Optional[str] = None) -> TraceSession:
        """Start a new trace session"""
        session = TraceSession(
            session_id=session_id,
            user_id=user_id,
            start_time=datetime.now(),
            end_time=None,
            decision_points=[],
            final_outcome=None,
            satisfaction_score=None
        )
        
        self.current_sessions[session_id] = session
        
        # Log to database
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO trace_sessions 
                (session_id, user_id, start_time, flagship_scenario)
                VALUES (?, ?, ?, ?)
            """, (session_id, user_id, session.start_time.isoformat(), flagship_scenario))
            await db.commit()
            
        return session
    
    async def log_decision_point(self, session_id: str, decision: DecisionPoint):
        """Log a decision point in the current session"""
        if session_id not in self.current_sessions:
            raise ValueError(f"No active session: {session_id}")
            
        session = self.current_sessions[session_id]
        session.decision_points.append(decision)
        
        # Log to database
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO decision_traces (
                    session_id, timestamp, decision_type,
                    beliefs_json, desires_json, tools_json,
                    tool_selected, reasoning_json, pattern_id,
                    expected_outcome_json, confidence_json, context_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                decision.timestamp.isoformat(),
                decision.decision_type,
                json.dumps(decision.beliefs_activated),
                json.dumps(decision.desires_prioritized),
                json.dumps(decision.tools_considered),
                decision.tool_selected,
                json.dumps(decision.reasoning_chain),
                decision.pattern_id,
                json.dumps(decision.outcome_expected),
                json.dumps(decision.confidence_scores),
                json.dumps(decision.context)
            ))
            
            # Update pattern effectiveness if applicable
            if decision.pattern_id:
                await self._update_pattern_usage(db, decision.pattern_id, decision.confidence_scores)
                
            await db.commit()
    
    async def log_belief_update(self, session_id: str, beliefs_before: Dict, 
                              beliefs_after: Dict, trigger: str, confidence: float):
        """Convenience method to log belief updates"""
        decision = DecisionPoint(
            timestamp=datetime.now(),
            decision_type='belief_update',
            beliefs_activated=beliefs_after,
            desires_prioritized=[],
            tools_considered=[],
            tool_selected=None,
            reasoning_chain=[f"Belief update triggered by: {trigger}"],
            pattern_id=None,
            outcome_expected={'beliefs_changed': list(set(beliefs_after.keys()) - set(beliefs_before.keys()))},
            confidence_scores={'update_confidence': confidence},
            context={'trigger': trigger, 'beliefs_before': beliefs_before}
        )
        
        await self.log_decision_point(session_id, decision)
    
    async def log_tool_selection(self, session_id: str, intention: str,
                                belief_state: Dict, tools_evaluated: List[Dict],
                                selected_tool: str, reasoning: str):
        """Convenience method to log tool selection"""
        decision = DecisionPoint(
            timestamp=datetime.now(),
            decision_type='tool_selection',
            beliefs_activated=belief_state,
            desires_prioritized=[],
            tools_considered=tools_evaluated,
            tool_selected=selected_tool,
            reasoning_chain=[reasoning],
            pattern_id=None,
            outcome_expected={'intention': intention},
            confidence_scores={tool['name']: tool['score'] for tool in tools_evaluated},
            context={'intention': intention}
        )
        
        await self.log_decision_point(session_id, decision)
        
        # Update tool selection patterns
        await self._update_tool_selection_pattern(
            intention, belief_state, selected_tool, 
            confidence_scores=decision.confidence_scores
        )
    
    async def end_session(self, session_id: str, final_outcome: Dict[str, Any],
                        satisfaction_score: Optional[float] = None):
        """End a trace session"""
        if session_id not in self.current_sessions:
            raise ValueError(f"No active session: {session_id}")
            
        session = self.current_sessions[session_id]
        session.end_time = datetime.now()
        session.final_outcome = final_outcome
        session.satisfaction_score = satisfaction_score
        
        # Update database
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE trace_sessions
                SET end_time = ?, decision_count = ?, 
                    final_outcome_json = ?, satisfaction_score = ?
                WHERE session_id = ?
            """, (
                session.end_time.isoformat(),
                len(session.decision_points),
                json.dumps(final_outcome),
                satisfaction_score,
                session_id
            ))
            await db.commit()
            
        # Clean up
        del self.current_sessions[session_id]
        
        return session
    
    async def _update_pattern_usage(self, db: aiosqlite.Connection, 
                                  pattern_id: str, confidence_scores: Dict[str, float]):
        """Update pattern effectiveness tracking"""
        avg_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.0
        
        await db.execute("""
            INSERT INTO pattern_effectiveness (pattern_id, usage_count, avg_confidence, last_used)
            VALUES (?, 1, ?, ?)
            ON CONFLICT(pattern_id) DO UPDATE SET
                usage_count = usage_count + 1,
                avg_confidence = (avg_confidence * usage_count + ?) / (usage_count + 1),
                last_used = ?
        """, (pattern_id, avg_confidence, datetime.now().isoformat(),
              avg_confidence, datetime.now().isoformat()))
    
    async def _update_tool_selection_pattern(self, intention: str, belief_state: Dict,
                                           tool_selected: str, confidence_scores: Dict[str, float]):
        """Update tool selection pattern tracking"""
        # Create a simple hash of belief state for grouping similar states
        belief_hash = self._hash_belief_state(belief_state)
        
        async with aiosqlite.connect(self.db_path) as db:
            avg_confidence = confidence_scores.get(tool_selected, 0.0)
            
            await db.execute("""
                INSERT INTO tool_selection_patterns 
                (intention, belief_state_hash, tool_selected, selection_count, avg_confidence)
                VALUES (?, ?, ?, 1, ?)
                ON CONFLICT(intention, belief_state_hash, tool_selected) DO UPDATE SET
                    selection_count = selection_count + 1,
                    avg_confidence = (avg_confidence * selection_count + ?) / (selection_count + 1)
            """, (intention, belief_hash, tool_selected, avg_confidence, avg_confidence))
            await db.commit()
    
    def _hash_belief_state(self, belief_state: Dict) -> str:
        """Create a hash of belief state for pattern matching"""
        # Extract key beliefs that affect tool selection
        key_beliefs = []
        
        for belief, value in sorted(belief_state.items()):
            if isinstance(value, dict) and value.get('confidence', 0) > 0.5:
                key_beliefs.append(f"{belief}:{value.get('value')}")
                
        return "|".join(key_beliefs) if key_beliefs else "default"
    
    async def get_pattern_effectiveness(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Get effectiveness metrics for a pattern"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT usage_count, success_count, avg_confidence, avg_satisfaction
                FROM pattern_effectiveness
                WHERE pattern_id = ?
            """, (pattern_id,)) as cursor:
                row = await cursor.fetchone()
                
                if row:
                    return {
                        'usage_count': row[0],
                        'success_count': row[1],
                        'success_rate': row[1] / row[0] if row[0] > 0 else 0,
                        'avg_confidence': row[2],
                        'avg_satisfaction': row[3]
                    }
                    
        return None
    
    async def get_tool_selection_insights(self, intention: str) -> List[Dict[str, Any]]:
        """Get insights about tool selection for a given intention"""
        insights = []
        
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT belief_state_hash, tool_selected, selection_count, 
                       success_rate, avg_confidence
                FROM tool_selection_patterns
                WHERE intention = ?
                ORDER BY selection_count DESC
                LIMIT 10
            """, (intention,)) as cursor:
                async for row in cursor:
                    insights.append({
                        'belief_pattern': row[0],
                        'tool': row[1],
                        'usage_count': row[2],
                        'success_rate': row[3],
                        'confidence': row[4]
                    })
                    
        return insights
    
    async def export_session_trace(self, session_id: str) -> Dict[str, Any]:
        """Export complete trace for a session"""
        trace_data = {
            'session_id': session_id,
            'decision_points': []
        }
        
        async with aiosqlite.connect(self.db_path) as db:
            # Get session info
            async with db.execute("""
                SELECT user_id, start_time, end_time, final_outcome_json, 
                       satisfaction_score, flagship_scenario
                FROM trace_sessions
                WHERE session_id = ?
            """, (session_id,)) as cursor:
                session_row = await cursor.fetchone()
                
                if session_row:
                    trace_data.update({
                        'user_id': session_row[0],
                        'start_time': session_row[1],
                        'end_time': session_row[2],
                        'final_outcome': json.loads(session_row[3]) if session_row[3] else None,
                        'satisfaction_score': session_row[4],
                        'flagship_scenario': session_row[5]
                    })
            
            # Get all decision points
            async with db.execute("""
                SELECT timestamp, decision_type, beliefs_json, desires_json,
                       tools_json, tool_selected, reasoning_json, pattern_id,
                       expected_outcome_json, confidence_json, context_json
                FROM decision_traces
                WHERE session_id = ?
                ORDER BY timestamp
            """, (session_id,)) as cursor:
                async for row in cursor:
                    trace_data['decision_points'].append({
                        'timestamp': row[0],
                        'decision_type': row[1],
                        'beliefs': json.loads(row[2]) if row[2] else {},
                        'desires': json.loads(row[3]) if row[3] else [],
                        'tools_considered': json.loads(row[4]) if row[4] else [],
                        'tool_selected': row[5],
                        'reasoning': json.loads(row[6]) if row[6] else [],
                        'pattern_id': row[7],
                        'expected_outcome': json.loads(row[8]) if row[8] else {},
                        'confidence_scores': json.loads(row[9]) if row[9] else {},
                        'context': json.loads(row[10]) if row[10] else {}
                    })
                    
        return trace_data