import sys
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
import questionary

console = Console()

BANNER_ART = """
 [bold cyan]===========================================================[/bold cyan]
   [bold yellow]Y O U T U B E   S E A R C H  &  D O W N L O A D E R[/bold yellow]
   [dim]Intelligent Multi-Format Media CLI System[/dim]
 [bold cyan]===========================================================[/bold cyan]
"""

FORMAT_OPTIONS = [
    {"name": "🎵 MP3 Audio (Recommended - 192kbps with ID3 tags & Album Art)", "value": "mp3"},
    {"name": "🎬 MP4 Video (High Quality HD Video)", "value": "mp4"},
    {"name": "🎶 M4A Audio (AAC)", "value": "m4a"},
    {"name": "🎼 FLAC Audio (Lossless)", "value": "flac"},
    {"name": "🔊 WAV Audio (Uncompressed)", "value": "wav"},
    {"name": "⚡ OPUS Audio (Web Quality)", "value": "opus"},
]


def print_header():
    """Print stylish CLI header banner."""
    console.print(BANNER_ART)


def print_warning(msg: str):
    """Print warning message."""
    console.print(f"[bold yellow]⚠️  {msg}[/bold yellow]")


def print_success(msg: str):
    """Print success message."""
    console.print(f"[bold green]✨ {msg}[/bold green]")


def print_error(msg: str):
    """Print error message."""
    console.print(f"[bold red]❌ {msg}[/bold red]")


def print_info(msg: str):
    """Print general info message."""
    console.print(f"[bold cyan]ℹ️  {msg}[/bold cyan]")


def prompt_format_selection(default_fmt: str = "mp3") -> str:
    """Prompt the user to select their desired target format at session start."""
    console.print("\n[bold magenta]Step 1: Choose Output Media Format[/bold magenta]")
    
    # Find matching choice index
    choices = [opt["name"] for opt in FORMAT_OPTIONS]
    
    selected_name = questionary.select(
        "Select format for this download session:",
        choices=choices,
        style=questionary.Style([
            ('qmark', 'fg:#5f87ff bold'),
            ('question', 'bold'),
            ('answer', 'fg:#5f87ff bold'),
            ('pointer', 'fg:#5f87ff bold'),
            ('highlighted', 'fg:#5f87ff bold'),
            ('selected', 'fg:#00d700 bold'),
        ])
    ).ask()

    if not selected_name:
        sys.exit(0)

    for opt in FORMAT_OPTIONS:
        if opt["name"] == selected_name:
            return opt["value"]

    return default_fmt


def prompt_search_query() -> str:
    """Prompt the user for natural language YouTube search prompt."""
    console.print("\n[bold magenta]Step 2: Enter Search Query or Playlist URL[/bold magenta]")
    console.print("[dim](Type 'back' or 'b' to change format, 'exit' or 'q' to quit)[/dim]")
    query = questionary.text(
        "Enter search prompt or YouTube playlist URL:",
        validate=lambda text: True if len(text.strip()) > 0 else "Please enter a search prompt."
    ).ask()
    
    if not query:
        sys.exit(0)
    
    clean_q = query.strip()
    if clean_q.lower() in ["back", "b", "/back", ":b"]:
        return "BACK"
    if clean_q.lower() in ["exit", "quit", "q"]:
        sys.exit(0)

    return clean_q


def display_ai_refinement(explanation: str, cleaned_query: str, format_choice: str):
    """Display how the rule-based AI engine refined the prompt."""
    panel_content = f"[bold green]Optimized Query:[/bold green] [yellow]\"{cleaned_query}\"[/yellow]\n" \
                    f"[bold green]Target Format:[/bold green] [cyan]{format_choice.upper()}[/cyan]\n" \
                    f"[dim]{explanation}[/dim]"
    console.print(Panel(panel_content, title="🤖 AI Prompt Refinement Engine", border_style="cyan"))


def display_search_results_table(results: List[Dict[str, Any]]):
    """Display YouTube search results in a rich formatted table."""
    table = Table(title="🔍 YouTube Search Results", show_lines=True, header_style="bold magenta")
    table.add_column("#", justify="center", style="cyan", no_wrap=True)
    table.add_column("Title", style="bold white", width=45)
    table.add_column("Channel / Uploader", style="yellow", width=25)
    table.add_column("Duration", justify="center", style="green", no_wrap=True)
    table.add_column("Views", justify="right", style="blue", no_wrap=True)

    for idx, item in enumerate(results, 1):
        table.add_row(
            str(idx),
            item["title"],
            item["uploader"],
            item["duration"],
            item["views"]
        )

    console.print(table)


def prompt_select_video(results: List[Dict[str, Any]]) -> Any:
    """Prompt user to select video(s), batch mode, or back options from search results."""
    console.print("\n[bold magenta]Step 3: Select Item(s) to Download[/bold magenta]")
    
    choices = [
        {"name": f"📦 BATCH MODE: Select Multiple / All ({len(results)} items)", "value": "BATCH_MODE"}
    ]
    for idx, item in enumerate(results):
        choices.append({
            "name": f"{idx+1}. {item['title']} [{item['duration']}] - ({item['uploader']})",
            "value": idx
        })
    
    choices.append({"name": "↩️  Back to Search / New Query", "value": "BACK_SEARCH"})
    choices.append({"name": "🔄 Change Output Format", "value": "BACK_FORMAT"})
    choices.append({"name": "❌ Cancel / Exit", "value": "CANCEL"})

    selected_choice = questionary.select(
        "Use arrow keys to choose a video, batch mode, or go back:",
        choices=choices
    ).ask()

    if selected_choice is None or selected_choice == "CANCEL":
        print_info("Session ended.")
        sys.exit(0)

    if selected_choice in ["BACK_SEARCH", "BACK_FORMAT"]:
        return selected_choice

    if selected_choice == "BATCH_MODE":
        return prompt_batch_checkbox_selection(results)

    return [results[selected_choice]]


def prompt_batch_checkbox_selection(results: List[Dict[str, Any]]) -> Any:
    """Interactive multi-select checkbox menu to pick multiple episodes/items in a batch."""
    console.print("\n[bold cyan]📦 Batch Selection: Use Spacebar to toggle, 'a' to toggle all, Enter to confirm[/bold cyan]")
    
    choices = [
        questionary.Choice(
            title=f"{idx+1}. {item['title']} [{item['duration']}]",
            value=idx,
            checked=True
        )
        for idx, item in enumerate(results)
    ]

    selected_indices = questionary.checkbox(
        "Select episodes/videos to download in this batch:",
        choices=choices
    ).ask()

    if selected_indices is None:
        return "BACK_SEARCH"

    if not selected_indices:
        print_info("No items selected for batch download.")
        return "BACK_SEARCH"

    return [results[i] for i in selected_indices]




def create_download_progress() -> Progress:
    """Create rich progress bar for yt-dlp downloading on a single dynamic line."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=30),
        "[progress.percentage]{task.percentage:>3.0f}%",
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=True
    )

