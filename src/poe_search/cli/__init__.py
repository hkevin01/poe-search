"""Command line interface for Poe Search."""

import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from poe_search import PoeSearchClient, __version__
from poe_search.utils.config import load_config, save_config
from poe_search.utils.token_manager import ensure_tokens_on_startup

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="poe-search")
@click.option("--config", type=click.Path(), help="Configuration file path")
@click.option("--token", help="Poe authentication token")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--skip-token-check", is_flag=True,
              help="Skip automatic token refresh check")
@click.pass_context
def main(ctx: click.Context, config: Optional[str], token: Optional[str],
         verbose: bool, skip_token_check: bool):
    """Poe Search - Search and organize your Poe.com conversations."""
    # Ensure that ctx.obj exists and is a dict
    ctx.ensure_object(dict)
    
    # Set up logging
    if verbose:
        import logging
        logging.basicConfig(level=logging.INFO)
    
    # Check tokens on startup unless skipped
    if not skip_token_check:
        console.print("🔄 Checking Poe.com authentication tokens...")
        success, tokens = ensure_tokens_on_startup(
            interactive=True, max_age_hours=36
        )
        
        if not success:
            console.print("❌ [red]Failed to obtain valid tokens[/red]")
            console.print("Run with --skip-token-check to bypass this check")
            sys.exit(1)
        else:
            console.print("✅ [green]Tokens are fresh and ready[/green]")
    
    # Load configuration
    config_path = Path(config) if config else None
    cfg = load_config(config_path)
    
    # Override with command line options
    if token:
        cfg.poe_token = token
    
    # Initialize client
    ctx.obj["client"] = PoeSearchClient(
        token=cfg.poe_token if cfg.poe_token else None,
        database_url=cfg.database_url,
        config_path=config_path,
        config=cfg,
    )
    ctx.obj["config"] = cfg


@main.group()
def config():
    """Configuration management commands."""
    pass


@config.command("set-token")
@click.argument("token")
@click.pass_context
def set_token(ctx: click.Context, token: str):
    """Set your Poe authentication token."""
    cfg = ctx.obj["config"]
    cfg.poe_token = token
    save_config(cfg, ctx.obj["client"].config_path)
    console.print("✅ Token saved successfully!", style="green")


@config.command("show")
@click.pass_context
def show_config(ctx: click.Context):
    """Show current configuration."""
    cfg = ctx.obj["config"]
    
    table = Table(title="Poe Search Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="magenta")
    
    for key, value in cfg.items():
        if key == "token" and value:
            value = f"{value[:8]}..." if len(value) > 8 else value
        table.add_row(key, str(value) if value else "Not set")
    
    console.print(table)


@main.command()
@click.argument("query")
@click.option("--bot", help="Filter by specific bot")
@click.option("--limit", default=10, help="Maximum number of results")
@click.option("--format", "output_format", default="table", type=click.Choice(["table", "json"]))
@click.pass_context
def search(ctx: click.Context, query: str, bot: Optional[str], limit: int, output_format: str):
    """Search your conversations."""
    client = ctx.obj["client"]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Searching conversations...", total=None)
        
        try:
            results = client.search(query=query, bot=bot, limit=limit)
            progress.update(task, completed=True)
        except Exception as e:
            console.print(f"❌ Search failed: {e}", style="red")
            return
    
    if not results:
        console.print("No conversations found matching your query.", style="yellow")
        return
    
    if output_format == "json":
        import json
        console.print(json.dumps(results, indent=2))
    else:
        table = Table(title=f"Search Results for '{query}'")
        table.add_column("ID", style="cyan")
        table.add_column("Bot", style="green")
        table.add_column("Preview", style="white", max_width=60)
        table.add_column("Date", style="blue")
        
        for result in results:
            table.add_row(
                str(result.get("id", "")),
                result.get("bot", ""),
                result.get("preview", "")[:60] + "..." if len(result.get("preview", "")) > 60 else result.get("preview", ""),
                result.get("date", ""),
            )
        
        console.print(table)
        console.print(f"\nFound {len(results)} results (showing first {limit})")


@main.command()
@click.option("--days", default=7, help="Number of days to sync")
@click.pass_context
def sync(ctx: click.Context, days: int):
    """Sync conversations from Poe."""
    client = ctx.obj["client"]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Syncing last {days} days...", total=None)
        
        try:
            stats = client.sync(days=days)
            progress.update(task, completed=True)
        except Exception as e:
            console.print(f"❌ Sync failed: {e}", style="red")
            return
    
    console.print("✅ Sync completed!", style="green")
    console.print(f"📊 New: {stats['new']}, Updated: {stats['updated']}, Total: {stats['total']}")


@main.group()
def bots():
    """Bot management commands."""
    pass


@bots.command("list")
@click.pass_context
def list_bots(ctx: click.Context):
    """List all bots you've chatted with."""
    client = ctx.obj["client"]
    
    try:
        bot_list = client.get_bots()
    except Exception as e:
        console.print(f"❌ Failed to get bots: {e}", style="red")
        return
    
    if not bot_list:
        console.print("No bots found in your conversation history.", style="yellow")
        return
    
    table = Table(title="Your Bots")
    table.add_column("Name", style="cyan")
    table.add_column("Display Name", style="green")
    table.add_column("Conversations", style="blue")
    table.add_column("Last Used", style="magenta")
    
    for bot in bot_list:
        table.add_row(
            bot.get("name", ""),
            bot.get("display_name", ""),
            str(bot.get("conversation_count", 0)),
            bot.get("last_used", ""),
        )
    
    console.print(table)


@main.command()
@click.option("--format", "output_format", default="json", type=click.Choice(["json", "csv", "markdown"]))
@click.option("--output", "-o", help="Output file path")
@click.option("--bot", help="Filter by specific bot")
@click.option("--days", type=int, help="Filter by number of days")
@click.option("--conversation-id", help="Export specific conversation")
@click.pass_context
def export(
    ctx: click.Context,
    output_format: str,
    output: Optional[str],
    bot: Optional[str],
    days: Optional[int],
    conversation_id: Optional[str],
):
    """Export conversations to file."""
    client = ctx.obj["client"]
    
    # Generate default output filename if not provided
    if not output:
        output = f"poe_conversations.{output_format}"
    
    filters = {}
    if bot:
        filters["bot"] = bot
    if days:
        filters["days"] = days
    if conversation_id:
        filters["conversation_id"] = conversation_id
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Exporting conversations...", total=None)
        
        try:
            client.export_conversations(
                output_path=output,
                format=output_format,
                **filters,
            )
            progress.update(task, completed=True)
        except Exception as e:
            console.print(f"❌ Export failed: {e}", style="red")
            return
    
    console.print(f"✅ Conversations exported to {output}", style="green")


@main.command()
@click.option("--period", default="month", type=click.Choice(["day", "week", "month", "year"]))
@click.pass_context
def analytics(ctx: click.Context, period: str):
    """Generate usage analytics."""
    client = ctx.obj["client"]
    
    try:
        data = client.get_analytics(period=period)
    except Exception as e:
        console.print(f"❌ Failed to generate analytics: {e}", style="red")
        return
    
    console.print(f"📊 Analytics for the last {period}")
    console.print(f"Total conversations: {data.get('total_conversations', 0)}")
    console.print(f"Active bots: {data.get('active_bots', 0)}")
    console.print(f"Messages sent: {data.get('messages_sent', 0)}")
    console.print(f"Average conversation length: {data.get('avg_conversation_length', 0):.1f}")


if __name__ == "__main__":
    main()
