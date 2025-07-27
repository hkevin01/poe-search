"""
Export service for conversation data.
"""

import json
import csv
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from ..core.models import Conversation, ExportOptions
from ..core.exceptions import ExportError
from ..core.utils import sanitize_filename, ensure_directory


class ExportService:
    """Service for exporting conversations in various formats."""

    def __init__(self):
        self.supported_formats = ['json', 'txt', 'csv', 'markdown']

    def export_conversations(
        self,
        conversations: List[Conversation],
        output_path: Path,
        options: ExportOptions
    ) -> bool:
        """
        Export conversations to file.

        Args:
            conversations: List of conversations to export
            output_path: Output file path
            options: Export options

        Returns:
            True if export successful

        Raises:
            ExportError: If export fails
        """
        try:
            # Ensure output directory exists
            if not ensure_directory(output_path.parent):
                raise ExportError(f"Cannot create output directory: {output_path.parent}")

            # Apply filters
            filtered_conversations = self._filter_conversations(conversations, options)

            if not filtered_conversations:
                raise ExportError("No conversations match the export criteria")

            # Export based on format
            if options.format == 'json':
                return self._export_json(filtered_conversations, output_path, options)
            elif options.format == 'txt':
                return self._export_txt(filtered_conversations, output_path, options)
            elif options.format == 'csv':
                return self._export_csv(filtered_conversations, output_path, options)
            elif options.format == 'markdown':
                return self._export_markdown(filtered_conversations, output_path, options)
            else:
                raise ExportError(f"Unsupported export format: {options.format}")

        except Exception as e:
            raise ExportError(f"Export failed: {str(e)}")

    def _filter_conversations(self, conversations: List[Conversation], options: ExportOptions) -> List[Conversation]:
        """Filter conversations based on export options."""
        filtered = conversations

        # Limit number of conversations
        if options.max_conversations:
            filtered = filtered[:options.max_conversations]

        # Filter by categories
        if options.categories:
            filtered = [conv for conv in filtered if conv.category in options.categories]

        # TODO: Add date range filtering when date parsing is implemented

        return filtered

    def _export_json(self, conversations: List[Conversation], output_path: Path, options: ExportOptions) -> bool:
        """Export conversations as JSON."""
        try:
            export_data = {
                'export_info': {
                    'timestamp': datetime.now().isoformat(),
                    'total_conversations': len(conversations),
                    'format': 'json',
                    'options': {
                        'include_metadata': options.include_metadata,
                        'include_timestamps': options.include_timestamps
                    }
                },
                'conversations': [conv.to_dict() for conv in conversations]
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            raise ExportError(f"JSON export failed: {str(e)}")

    def _export_txt(self, conversations: List[Conversation], output_path: Path, options: ExportOptions) -> bool:
        """Export conversations as plain text."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Poe Search Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Conversations: {len(conversations)}\n")
                f.write("=" * 80 + "\n\n")

                for i, conv in enumerate(conversations, 1):
                    f.write(f"[{i}] {conv.title}\n")

                    if options.include_metadata:
                        f.write(f"Bot: {conv.bot}\n")
                        f.write(f"Category: {conv.category}\n")
                        f.write(f"URL: {conv.url}\n")
                        f.write(f"Extracted: {conv.extracted_at}\n")

                    f.write("-" * 40 + "\n")

                    for msg in conv.messages:
                        role_indicator = "👤 USER" if msg.role == 'user' else "🤖 ASSISTANT"
                        f.write(f"{role_indicator}: {msg.content}\n\n")

                    f.write("=" * 80 + "\n\n")

            return True
        except Exception as e:
            raise ExportError(f"Text export failed: {str(e)}")

    def _export_csv(self, conversations: List[Conversation], output_path: Path, options: ExportOptions) -> bool:
        """Export conversations as CSV."""
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Write header
                headers = ['conversation_id', 'title', 'bot', 'category', 'message_count']
                if options.include_metadata:
                    headers.extend(['url', 'method', 'extracted_at'])
                if options.include_timestamps:
                    headers.append('first_message_time')

                writer.writerow(headers)

                # Write conversation data
                for conv in conversations:
                    row = [
                        conv.id,
                        conv.title,
                        conv.bot,
                        conv.category,
                        len(conv.messages)
                    ]

                    if options.include_metadata:
                        row.extend([conv.url, conv.method, conv.extracted_at])

                    if options.include_timestamps and conv.messages:
                        row.append(conv.messages[0].timestamp or '')

                    writer.writerow(row)

            return True
        except Exception as e:
            raise ExportError(f"CSV export failed: {str(e)}")

    def _export_markdown(self, conversations: List[Conversation], output_path: Path, options: ExportOptions) -> bool:
        """Export conversations as Markdown."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("# Poe Search Export\n\n")
                f.write(f"**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
                f.write(f"**Total Conversations:** {len(conversations)}  \n\n")
                f.write("---\n\n")

                for i, conv in enumerate(conversations, 1):
                    f.write(f"## {i}. {conv.title}\n\n")

                    if options.include_metadata:
                        f.write(f"**Bot:** {conv.bot}  \n")
                        f.write(f"**Category:** {conv.category}  \n")
                        f.write(f"**URL:** [{conv.url}]({conv.url})  \n")
                        f.write(f"**Extracted:** {conv.extracted_at}  \n\n")

                    if conv.messages:
                        f.write("### Messages\n\n")
                        for msg in conv.messages:
                            role_badge = "👤 **User**" if msg.role == 'user' else "🤖 **Assistant**"
                            f.write(f"{role_badge}:\n")
                            f.write(f"{msg.content}\n\n")

                    f.write("---\n\n")

            return True
        except Exception as e:
            raise ExportError(f"Markdown export failed: {str(e)}")

    def get_export_filename(self, base_name: str, format_type: str) -> str:
        """Generate a safe export filename."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = sanitize_filename(base_name)
        return f"{safe_name}_{timestamp}.{format_type}"
