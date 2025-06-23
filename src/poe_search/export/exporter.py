"""Export conversations to various formats."""

import json
import csv
import logging
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ConversationExporter:
    """Export conversations to various formats."""
    
    def __init__(self, database):
        """Initialize the exporter.
        
        Args:
            database: Database instance
        """
        self.database = database
    
    def export(
        self,
        conversations: List[Dict[str, Any]],
        output_path: str,
        format: str = "json",
    ) -> None:
        """Export conversations to the specified format.
        
        Args:
            conversations: List of conversations to export
            output_path: Output file path
            format: Export format (json, csv, markdown)
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Exporting {len(conversations)} conversations to {output_path} as {format}")
        
        if format.lower() == "json":
            self._export_json(conversations, output_file)
        elif format.lower() == "csv":
            self._export_csv(conversations, output_file)
        elif format.lower() == "markdown":
            self._export_markdown(conversations, output_file)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_json(self, conversations: List[Dict[str, Any]], output_file: Path) -> None:
        """Export conversations as JSON.
        
        Args:
            conversations: List of conversations
            output_file: Output file path
        """
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "conversation_count": len(conversations),
            "conversations": conversations,
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    def _export_csv(self, conversations: List[Dict[str, Any]], output_file: Path) -> None:
        """Export conversations as CSV.
        
        Args:
            conversations: List of conversations
            output_file: Output file path
        """
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                "conversation_id",
                "bot",
                "title",
                "created_at",
                "updated_at",
                "message_count",
                "message_id",
                "role",
                "content",
                "timestamp",
            ])
            
            # Write data
            for conversation in conversations:
                base_row = [
                    conversation.get("id", ""),
                    conversation.get("bot", ""),
                    conversation.get("title", ""),
                    conversation.get("created_at", ""),
                    conversation.get("updated_at", ""),
                    conversation.get("message_count", 0),
                ]
                
                # If conversation has messages, write each message as a row
                messages = conversation.get("messages", [])
                if messages:
                    for message in messages:
                        message_row = base_row + [
                            message.get("id", ""),
                            message.get("role", ""),
                            message.get("content", ""),
                            message.get("timestamp", ""),
                        ]
                        writer.writerow(message_row)
                else:
                    # Write conversation without messages
                    writer.writerow(base_row + ["", "", "", ""])
    
    def _export_markdown(self, conversations: List[Dict[str, Any]], output_file: Path) -> None:
        """Export conversations as Markdown.
        
        Args:
            conversations: List of conversations
            output_file: Output file path
        """
        with open(output_file, "w", encoding="utf-8") as f:
            # Write header
            f.write("# Poe Conversations Export\n\n")
            f.write(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total conversations: {len(conversations)}\n\n")
            f.write("---\n\n")
            
            # Write each conversation
            for i, conversation in enumerate(conversations, 1):
                f.write(f"## Conversation {i}: {conversation.get('title', 'Untitled')}\n\n")
                
                # Conversation metadata
                f.write(f"- **Bot**: {conversation.get('bot', 'Unknown')}\n")
                f.write(f"- **Created**: {conversation.get('created_at', 'Unknown')}\n")
                f.write(f"- **Updated**: {conversation.get('updated_at', 'Unknown')}\n")
                f.write(f"- **Messages**: {conversation.get('message_count', 0)}\n")
                f.write(f"- **ID**: `{conversation.get('id', 'Unknown')}`\n\n")
                
                # Write messages
                messages = conversation.get("messages", [])
                if messages:
                    f.write("### Messages\n\n")
                    
                    for message in messages:
                        role = message.get("role", "unknown")
                        content = message.get("content", "")
                        timestamp = message.get("timestamp", "")
                        
                        # Format role
                        if role == "user":
                            role_emoji = "👤"
                            role_text = "User"
                        elif role == "bot":
                            role_emoji = "🤖"
                            role_text = conversation.get("bot", "Bot")
                        else:
                            role_emoji = "❓"
                            role_text = role.title()
                        
                        f.write(f"#### {role_emoji} {role_text}\n")
                        if timestamp:
                            f.write(f"*{timestamp}*\n\n")
                        
                        # Format content (escape markdown special characters)
                        escaped_content = content.replace("*", "\\*").replace("_", "\\_").replace("`", "\\`")
                        f.write(f"{escaped_content}\n\n")
                else:
                    f.write("*No messages in this conversation*\n\n")
                
                f.write("---\n\n")
    
    def export_search_results(
        self,
        results: List[Dict[str, Any]],
        output_path: str,
        query: str,
        format: str = "markdown",
    ) -> None:
        """Export search results with highlighting.
        
        Args:
            results: Search results
            output_path: Output file path
            query: Original search query
            format: Export format
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == "markdown":
            self._export_search_results_markdown(results, output_file, query)
        elif format.lower() == "json":
            export_data = {
                "query": query,
                "exported_at": datetime.now().isoformat(),
                "result_count": len(results),
                "results": results,
            }
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
        else:
            # Fallback to regular export
            self.export(results, output_path, format)
    
    def _export_search_results_markdown(
        self,
        results: List[Dict[str, Any]],
        output_file: Path,
        query: str,
    ) -> None:
        """Export search results as Markdown with query highlighting.
        
        Args:
            results: Search results
            output_file: Output file path
            query: Search query
        """
        with open(output_file, "w", encoding="utf-8") as f:
            # Write header
            f.write(f"# Search Results for: \"{query}\"\n\n")
            f.write(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Results found: {len(results)}\n\n")
            f.write("---\n\n")
            
            # Write each result
            for i, result in enumerate(results, 1):
                f.write(f"## Result {i}\n\n")
                
                # Result metadata
                f.write(f"- **Conversation**: {result.get('title', 'Untitled')}\n")
                f.write(f"- **Bot**: {result.get('bot', 'Unknown')}\n")
                f.write(f"- **Date**: {result.get('date', 'Unknown')}\n")
                f.write(f"- **Score**: {result.get('score', 0):.2f}\n")
                f.write(f"- **ID**: `{result.get('id', 'Unknown')}`\n\n")
                
                # Preview with query highlighted
                preview = result.get("preview", "")
                if preview and query:
                    # Simple highlighting - wrap query in bold
                    highlighted_preview = preview.replace(
                        query,
                        f"**{query}**",
                    )
                    f.write(f"### Preview\n\n{highlighted_preview}\n\n")
                
                # Write matching messages if available
                matches = result.get("matches", [])
                if matches:
                    f.write(f"### Matching Messages ({len(matches)})\n\n")
                    
                    for match in matches[:3]:  # Show first 3 matches
                        role = match.get("role", "unknown")
                        content = match.get("content", "")
                        timestamp = match.get("timestamp", "")
                        
                        # Highlight query in content
                        if query and content:
                            highlighted_content = content.replace(
                                query,
                                f"**{query}**",
                            )
                        else:
                            highlighted_content = content
                        
                        f.write(f"**{role.title()}** ({timestamp}):\n")
                        f.write(f"{highlighted_content[:200]}...\n\n")
                    
                    if len(matches) > 3:
                        f.write(f"*...and {len(matches) - 3} more matches*\n\n")
                
                f.write("---\n\n")
