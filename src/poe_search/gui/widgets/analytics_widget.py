"""Analytics widget for displaying conversation statistics and insights."""

import logging
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class StatCard(QFrame):
    """Widget for displaying a single statistic."""
    
    def __init__(self, title: str, value: str, subtitle: str = "", parent=None):
        """Initialize stat card."""
        super().__init__(parent)
        
        self.title = title
        self.value = value
        self.subtitle = subtitle
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the stat card UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #888888;
                font-weight: 500;
            }
        """)
        layout.addWidget(title_label)
        
        # Value
        value_label = QLabel(self.value)
        value_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #ffffff;
                font-weight: 600;
                margin: 4px 0;
            }
        """)
        layout.addWidget(value_label)
        
        # Subtitle
        if self.subtitle:
            subtitle_label = QLabel(self.subtitle)
            subtitle_label.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: #888888;
                }
            """)
            layout.addWidget(subtitle_label)
        
        # Style the frame
        self.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 8px;
            }
        """)
        
        self.setFixedHeight(100)
    
    def update_value(self, value: str, subtitle: str = ""):
        """Update the stat card value."""
        self.value = value
        self.subtitle = subtitle
        
        # Update labels (find them by type)
        labels = self.findChildren(QLabel)
        if len(labels) >= 2:
            labels[1].setText(value)  # Value label
            if len(labels) >= 3 and subtitle:
                labels[2].setText(subtitle)  # Subtitle label


class AnalyticsWidget(QWidget):
    """Widget for displaying conversation analytics and statistics."""
    
    # Signals
    refresh_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the analytics widget."""
        super().__init__(parent)
        
        self.conversations = []
        self.client = None
        self.setup_ui()
        self.setup_connections()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_analytics)
        
    def set_client(self, client):
        """Set the Poe Search client.
        
        Args:
            client: PoeSearchClient instance
        """
        self.client = client
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems([
            "Last 7 days", "Last 30 days", "Last 90 days", 
            "Last year", "All time"
        ])
        self.time_range_combo.setCurrentText("Last 30 days")
        controls_layout.addWidget(QLabel("Time Range:"))
        controls_layout.addWidget(self.time_range_combo)
        
        controls_layout.addStretch()
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setMinimumHeight(32)
        controls_layout.addWidget(self.refresh_button)
        
        self.auto_refresh_checkbox = QPushButton("Auto-refresh: OFF")
        self.auto_refresh_checkbox.setCheckable(True)
        self.auto_refresh_checkbox.setMinimumHeight(32)
        controls_layout.addWidget(self.auto_refresh_checkbox)
        
        layout.addLayout(controls_layout)
        
        # Stats cards
        stats_group = self.create_stats_section()
        layout.addWidget(stats_group)
        
        # Charts and breakdowns
        charts_layout = QHBoxLayout()
        
        # Category breakdown
        category_group = self.create_category_breakdown()
        charts_layout.addWidget(category_group, 1)
        
        # Bot usage
        bot_group = self.create_bot_breakdown()
        charts_layout.addWidget(bot_group, 1)
        
        layout.addLayout(charts_layout)
        
        # Activity timeline
        timeline_group = self.create_timeline_section()
        layout.addWidget(timeline_group)
        
    def create_stats_section(self) -> QGroupBox:
        """Create the overview statistics section."""
        group = QGroupBox("Overview Statistics")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                padding-top: 12px;
                margin-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
            }
        """)
        
        layout = QGridLayout(group)
        layout.setSpacing(12)
        
        # Create stat cards
        self.total_conversations_card = StatCard("Total Conversations", "0")
        self.total_messages_card = StatCard("Total Messages", "0")
        self.avg_messages_card = StatCard("Avg Messages per Conversation", "0")
        self.most_used_bot_card = StatCard("Most Used Bot", "None")
        self.recent_activity_card = StatCard("Recent Activity", "0", "conversations this week")
        self.largest_conversation_card = StatCard("Largest Conversation", "0", "messages")
        
        # Add cards to grid
        layout.addWidget(self.total_conversations_card, 0, 0)
        layout.addWidget(self.total_messages_card, 0, 1)
        layout.addWidget(self.avg_messages_card, 0, 2)
        layout.addWidget(self.most_used_bot_card, 1, 0)
        layout.addWidget(self.recent_activity_card, 1, 1)
        layout.addWidget(self.largest_conversation_card, 1, 2)
        
        return group
    
    def create_category_breakdown(self) -> QGroupBox:
        """Create category breakdown section."""
        group = QGroupBox("Conversations by Category")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                padding-top: 12px;
                margin-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        self.category_table = QTableWidget()
        self.category_table.setColumnCount(3)
        self.category_table.setHorizontalHeaderLabels(["Category", "Count", "Percentage"])
        
        # Configure table
        self.category_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.category_table.setSortingEnabled(True)
        self.category_table.setAlternatingRowColors(True)
        
        # Column sizing
        header = self.category_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        # Style
        self.category_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #404040;
                font-size: 12px;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 6px;
                border: none;
            }
            QHeaderView::section {
                background-color: #3d3d3d;
                color: #ffffff;
                padding: 8px;
                border: none;
                border-right: 1px solid #404040;
                font-weight: 600;
                font-size: 11px;
            }
        """)
        
        layout.addWidget(self.category_table)
        
        return group
    
    def create_bot_breakdown(self) -> QGroupBox:
        """Create bot usage breakdown section."""
        group = QGroupBox("Conversations by Bot")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                padding-top: 12px;
                margin-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        self.bot_table = QTableWidget()
        self.bot_table.setColumnCount(3)
        self.bot_table.setHorizontalHeaderLabels(["Bot", "Count", "Percentage"])
        
        # Configure table
        self.bot_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.bot_table.setSortingEnabled(True)
        self.bot_table.setAlternatingRowColors(True)
        
        # Column sizing
        header = self.bot_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        # Style
        self.bot_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #404040;
                font-size: 12px;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 6px;
                border: none;
            }
            QHeaderView::section {
                background-color: #3d3d3d;
                color: #ffffff;
                padding: 8px;
                border: none;
                border-right: 1px solid #404040;
                font-weight: 600;
                font-size: 11px;
            }
        """)
        
        layout.addWidget(self.bot_table)
        
        return group
    
    def create_timeline_section(self) -> QGroupBox:
        """Create activity timeline section."""
        group = QGroupBox("Activity Timeline")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                padding-top: 12px;
                margin-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        self.timeline_table = QTableWidget()
        self.timeline_table.setColumnCount(4)
        self.timeline_table.setHorizontalHeaderLabels([
            "Date", "Conversations", "Messages", "Most Active Bot"
        ])
        
        # Configure table
        self.timeline_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.timeline_table.setSortingEnabled(True)
        self.timeline_table.setAlternatingRowColors(True)
        
        # Column sizing
        header = self.timeline_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        # Style
        self.timeline_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #404040;
                font-size: 12px;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 6px;
                border: none;
            }
            QHeaderView::section {
                background-color: #3d3d3d;
                color: #ffffff;
                padding: 8px;
                border: none;
                border-right: 1px solid #404040;
                font-weight: 600;
                font-size: 11px;
            }
        """)
        
        layout.addWidget(self.timeline_table)
        
        return group
    
    def setup_connections(self):
        """Set up signal connections."""
        self.time_range_combo.currentTextChanged.connect(self.on_time_range_changed)
        self.refresh_button.clicked.connect(self.refresh_analytics)
        self.auto_refresh_checkbox.toggled.connect(self.toggle_auto_refresh)
    
    def update_analytics(self, conversations: List[Dict[str, Any]]):
        """Update analytics with conversation data."""
        self.conversations = conversations
        
        # Filter by time range
        filtered_conversations = self.filter_by_time_range(conversations)
        
        # Update overview stats
        self.update_overview_stats(filtered_conversations)
        
        # Update category breakdown
        self.update_category_breakdown(filtered_conversations)
        
        # Update bot breakdown
        self.update_bot_breakdown(filtered_conversations)
        
        # Update timeline
        self.update_timeline(filtered_conversations)
    
    def filter_by_time_range(self, conversations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter conversations by selected time range."""
        time_range = self.time_range_combo.currentText()
        
        if time_range == "All time":
            return conversations
        
        # Calculate date threshold
        now = datetime.now()
        if time_range == "Last 7 days":
            threshold = now - timedelta(days=7)
        elif time_range == "Last 30 days":
            threshold = now - timedelta(days=30)
        elif time_range == "Last 90 days":
            threshold = now - timedelta(days=90)
        elif time_range == "Last year":
            threshold = now - timedelta(days=365)
        else:
            return conversations
        
        # Filter conversations
        filtered = []
        for conv in conversations:
            created_at = conv.get("created_at", "")
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if dt >= threshold:
                        filtered.append(conv)
                except:
                    continue
        
        return filtered
    
    def update_overview_stats(self, conversations: List[Dict[str, Any]]):
        """Update overview statistics cards."""
        if not conversations:
            self.total_conversations_card.update_value("0")
            self.total_messages_card.update_value("0")
            self.avg_messages_card.update_value("0")
            self.most_used_bot_card.update_value("None")
            self.recent_activity_card.update_value("0", "conversations this week")
            self.largest_conversation_card.update_value("0", "messages")
            return
        
        total_conversations = len(conversations)
        total_messages = sum(conv.get("message_count", 0) for conv in conversations)
        avg_messages = total_messages / total_conversations if total_conversations > 0 else 0
        
        # Most used bot
        bot_counts = Counter(conv.get("bot", "Unknown") for conv in conversations)
        most_used_bot = bot_counts.most_common(1)[0][0] if bot_counts else "None"
        
        # Recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_conversations = 0
        for conv in conversations:
            created_at = conv.get("created_at", "")
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if dt >= week_ago:
                        recent_conversations += 1
                except:
                    continue
        
        # Largest conversation
        largest_conversation = max(conversations, key=lambda x: x.get("message_count", 0))
        largest_count = largest_conversation.get("message_count", 0)
        
        # Update cards
        self.total_conversations_card.update_value(f"{total_conversations:,}")
        self.total_messages_card.update_value(f"{total_messages:,}")
        self.avg_messages_card.update_value(f"{avg_messages:.1f}")
        self.most_used_bot_card.update_value(most_used_bot)
        self.recent_activity_card.update_value(str(recent_conversations), "conversations this week")
        self.largest_conversation_card.update_value(str(largest_count), "messages")
    
    def update_category_breakdown(self, conversations: List[Dict[str, Any]]):
        """Update category breakdown table."""
        category_counts = Counter(conv.get("category", "Uncategorized") for conv in conversations)
        total = len(conversations)
        
        self.category_table.setRowCount(len(category_counts))
        
        for row, (category, count) in enumerate(category_counts.most_common()):
            percentage = (count / total * 100) if total > 0 else 0
            
            self.category_table.setItem(row, 0, QTableWidgetItem(category))
            self.category_table.setItem(row, 1, QTableWidgetItem(str(count)))
            self.category_table.setItem(row, 2, QTableWidgetItem(f"{percentage:.1f}%"))
    
    def update_bot_breakdown(self, conversations: List[Dict[str, Any]]):
        """Update bot breakdown table."""
        bot_counts = Counter(conv.get("bot", "Unknown") for conv in conversations)
        total = len(conversations)
        
        self.bot_table.setRowCount(len(bot_counts))
        
        for row, (bot, count) in enumerate(bot_counts.most_common()):
            percentage = (count / total * 100) if total > 0 else 0
            
            self.bot_table.setItem(row, 0, QTableWidgetItem(bot))
            self.bot_table.setItem(row, 1, QTableWidgetItem(str(count)))
            self.bot_table.setItem(row, 2, QTableWidgetItem(f"{percentage:.1f}%"))
    
    def update_timeline(self, conversations: List[Dict[str, Any]]):
        """Update activity timeline table."""
        # Group conversations by date
        daily_activity = defaultdict(lambda: {"conversations": 0, "messages": 0, "bots": []})
        
        for conv in conversations:
            created_at = conv.get("created_at", "")
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    date_key = dt.strftime("%Y-%m-%d")
                    
                    daily_activity[date_key]["conversations"] += 1
                    daily_activity[date_key]["messages"] += conv.get("message_count", 0)
                    daily_activity[date_key]["bots"].append(conv.get("bot", "Unknown"))
                except:
                    continue
        
        # Sort by date (most recent first)
        sorted_dates = sorted(daily_activity.keys(), reverse=True)[:30]  # Last 30 days
        
        self.timeline_table.setRowCount(len(sorted_dates))
        
        for row, date in enumerate(sorted_dates):
            activity = daily_activity[date]
            
            # Most active bot for the day
            bot_counts = Counter(activity["bots"])
            most_active_bot = bot_counts.most_common(1)[0][0] if bot_counts else "None"
            
            self.timeline_table.setItem(row, 0, QTableWidgetItem(date))
            self.timeline_table.setItem(row, 1, QTableWidgetItem(str(activity["conversations"])))
            self.timeline_table.setItem(row, 2, QTableWidgetItem(str(activity["messages"])))
            self.timeline_table.setItem(row, 3, QTableWidgetItem(most_active_bot))
    
    def on_time_range_changed(self, time_range: str):
        """Handle time range change."""
        if self.conversations:
            self.update_analytics(self.conversations)
    
    def refresh_analytics(self):
        """Refresh analytics data."""
        logger.debug("AnalyticsWidget.refresh_analytics() called")
        try:
            self.refresh_requested.emit()
            logger.debug("AnalyticsWidget.refresh_analytics() completed successfully")
        except Exception as e:
            logger.error(f"Error in AnalyticsWidget.refresh_analytics(): {e}")
            raise
    
    def toggle_auto_refresh(self, enabled: bool):
        """Toggle auto-refresh functionality."""
        if enabled:
            self.auto_refresh_checkbox.setText("Auto-refresh: ON")
            self.refresh_timer.start(60000)  # 1 minute
        else:
            self.auto_refresh_checkbox.setText("Auto-refresh: OFF")
            self.refresh_timer.stop()

    def refresh_data(self):
        """Refresh analytics data (alias for refresh_analytics)."""
        logger.debug("AnalyticsWidget.refresh_data() called")
        try:
            # Don't call refresh_analytics() to avoid recursion
            # Instead, directly emit the signal or update the data
            if self.client:
                # Get conversations and update analytics directly
                conversations = self.client.get_conversations()
                self.update_analytics(conversations)
            logger.debug("AnalyticsWidget.refresh_data() completed successfully")
        except Exception as e:
            logger.error(f"Error in AnalyticsWidget.refresh_data(): {e}")
            raise
