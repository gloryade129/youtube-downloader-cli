import sys
import os
import click
from pathlib import Path
from typing import Optional, Any

from yt_downloader.config import load_config, save_config, check_ffmpeg
from yt_downloader.query_refiner import refine_query
from yt_downloader.youtube_engine import search_youtube, download_media, is_playlist_url, fetch_playlist_info
from yt_downloader.metadata_tagger import embed_metadata_and_artwork
from yt_downloader.ui import (
    print_header,
    print_info,
    print_success,
    print_warning,
    print_error,
    prompt_format_selection,
    prompt_search_query,
    display_ai_refinement,
    display_search_results_table,
    prompt_select_video,
    prompt_batch_checkbox_selection,
    create_download_progress,
    console,
)


@click.group(invoke_without_command=True)
@click.option("--format", "-f", "fmt_opt", help="Target media format (mp3, mp4, m4a, flac, wav)")
@click.option("--output", "-o", "output_dir", help="Output directory path")
@click.option("--limit", "-l", default=5, type=int, help="Number of search results to fetch")
@click.pass_context
def cli(ctx, fmt_opt: Optional[str], output_dir: Optional[str], limit: int):
    """YouTube Search & Multi-Format Downloader CLI System."""
    if ctx.invoked_subcommand is None:
        run_interactive_session(fmt_opt=fmt_opt, output_dir=output_dir, limit=limit)


@cli.command()
@click.argument("query")
@click.option("--format", "-f", "fmt_opt", default="mp3", help="Target media format (mp3, mp4, m4a, flac, wav)")
@click.option("--output", "-o", "output_dir", help="Output directory path")
@click.option("--limit", "-l", default=5, type=int, help="Number of search results")
def search(query: str, fmt_opt: str, output_dir: Optional[str], limit: int):
    """Search YouTube and download a video or batch by prompt."""
    config = load_config()
    target_output = output_dir or config.get("download_dir", "./downloads")
    
    print_header()
    ffmpeg_ok, ffmpeg_path = check_ffmpeg()
    if not ffmpeg_ok:
        print_warning("ffmpeg not detected on system PATH. Pre-merged media stream will be downloaded automatically.")

    if is_playlist_url(query):
        execute_playlist_download(query, fmt_opt, target_output, ffmpeg_path)
        return

    # Refine query
    refined = refine_query(query, current_format=fmt_opt)
    display_ai_refinement(refined.explanation, refined.cleaned_query, fmt_opt)

    # Search YouTube
    with console.status("[bold cyan]Searching YouTube...[/bold cyan]", spinner="dots"):
        results = search_youtube(refined.cleaned_query, limit=limit)

    if not results:
        print_error("No YouTube results found for your query.")
        return

    display_search_results_table(results)
    selected_items = prompt_select_video(results)

    if isinstance(selected_items, list):
        execute_batch_download(selected_items, fmt_opt, target_output, ffmpeg_path)


@cli.command()
@click.argument("url")
@click.option("--format", "-f", "fmt_opt", default="mp3", help="Target media format (mp3, mp4, m4a, flac)")
@click.option("--output", "-o", "output_dir", help="Output directory path")
def download(url: str, fmt_opt: str, output_dir: Optional[str]):
    """Directly download a YouTube video or playlist from a URL."""
    config = load_config()
    target_output = output_dir or config.get("download_dir", "./downloads")
    
    print_header()
    ffmpeg_ok, ffmpeg_path = check_ffmpeg()

    if is_playlist_url(url):
        execute_playlist_download(url, fmt_opt, target_output, ffmpeg_path)
    else:
        item = {"title": "Direct URL Media", "url": url, "uploader": "YouTube"}
        execute_download(item, fmt_opt, target_output, ffmpeg_path)


@cli.command(name="playlist")
@click.argument("url")
@click.option("--format", "-f", "fmt_opt", default="mp3", help="Target media format (mp3, mp4, m4a, flac)")
@click.option("--output", "-o", "output_dir", help="Output directory path")
def playlist_cmd(url: str, fmt_opt: str, output_dir: Optional[str]):
    """Fetch and batch download all videos or episodes in a YouTube Playlist."""
    config = load_config()
    target_output = output_dir or config.get("download_dir", "./downloads")
    
    print_header()
    ffmpeg_ok, ffmpeg_path = check_ffmpeg()
    execute_playlist_download(url, fmt_opt, target_output, ffmpeg_path)


@cli.command(name="config")
@click.option("--show", is_flag=True, help="Display current configuration")
@click.option("--set-dir", help="Set default download directory")
@click.option("--set-format", help="Set default target media format")
def configure(show: bool, set_dir: Optional[str], set_format: Optional[str]):
    """View or update CLI settings."""
    config = load_config()
    
    if set_dir:
        config["download_dir"] = os.path.abspath(set_dir)
        save_config(config)
        print_success(f"Default download directory updated to: {config['download_dir']}")

    if set_format:
        config["default_format"] = set_format.lower()
        save_config(config)
        print_success(f"Default format updated to: {config['default_format']}")

    if show or (not set_dir and not set_format):
        console.print("[bold magenta]Current YouTube CLI Configuration:[/bold magenta]")
        for k, v in config.items():
            console.print(f"  [bold cyan]{k}:[/bold cyan] [yellow]{v}[/yellow]")


def execute_playlist_download(playlist_url: str, target_format: str, output_dir: str, ffmpeg_path: Optional[str]) -> Any:
    """Fetch playlist info and interactively prompt user to select episodes to download in a batch."""
    with console.status("[bold cyan]Fetching Playlist & Episode details...[/bold cyan]", spinner="dots"):
        playlist = fetch_playlist_info(playlist_url)

    entries = playlist.get("entries", [])
    title = playlist.get("title", "Playlist")

    if not entries:
        print_error(f"No videos or episodes found in playlist '{title}'.")
        return "BACK_SEARCH"

    console.print(f"\n[bold green]📦 Found Playlist / Show Batch:[/bold green] [yellow]\"{title}\"[/yellow] ([cyan]{len(entries)} items/episodes[/cyan])")
    display_search_results_table(entries)

    selected_items = prompt_batch_checkbox_selection(entries)
    if isinstance(selected_items, list):
        execute_batch_download(selected_items, target_format, output_dir, ffmpeg_path)
    return selected_items


def execute_batch_download(items: list, target_format: str, output_dir: str, ffmpeg_path: Optional[str]):
    """Batch download multiple selected items/episodes with overall counter."""
    total = len(items)
    console.print(f"\n[bold magenta]🚀 Starting Batch Download of {total} item(s)...[/bold magenta]\n")

    for idx, item in enumerate(items, 1):
        console.print(f"[bold cyan]-----------------------------------------------------------[/bold cyan]")
        console.print(f"[bold yellow]Batch Item [{idx}/{total}]:[/bold yellow] [bold white]{item.get('title')}[/bold white]")
        execute_download(item, target_format, output_dir, ffmpeg_path)

    print_success(f"\n🎉 Batch download of all {total} item(s) completed successfully!")
    print_info(f"📁 All files saved to your laptop at: [bold yellow]{os.path.abspath(output_dir)}[/bold yellow]")


def execute_download(item: dict, target_format: str, output_dir: str, ffmpeg_path: Optional[str]):
    """Execute download of selected video item and handle progress display & ID3 metadata tagging."""
    title = item.get("title", "Download")
    url = item.get("url")
    uploader = item.get("uploader", "Unknown Artist")
    thumbnail = item.get("thumbnail")

    print_info(f"Downloading: [bold white]{title}[/bold white] -> [cyan]{target_format.upper()}[/cyan]")
    print_info(f"Location: [dim]{output_dir}[/dim]")

    task_id = None
    progress = create_download_progress()

    def ytdl_progress_hook(d):
        nonlocal task_id
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            filename = os.path.basename(d.get("filename", "File"))
            
            if task_id is None:
                task_id = progress.add_task(f"Downloading {filename[:25]}...", total=total)
            else:
                progress.update(task_id, completed=downloaded, total=total)
        elif d["status"] == "finished":
            if task_id is not None:
                progress.update(task_id, description="Processing media conversion...")

    with progress:
        try:
            result = download_media(
                url=url,
                output_dir=output_dir,
                target_format=target_format,
                ffmpeg_path=ffmpeg_path,
                progress_hook=ytdl_progress_hook
            )
            filepath = result.get("filepath")
        except Exception as e:
            print_error(f"Download failed for '{title}': {e}")
            return

    print_success(f"Saved: [bold yellow]{filepath}[/bold yellow]")

    # Tag MP3 files with ID3 tags & artwork thumbnail
    if target_format.lower() == "mp3" and filepath and os.path.exists(filepath):
        embed_metadata_and_artwork(
            file_path=filepath,
            title=title,
            artist=uploader,
            album=uploader,
            thumbnail_url=thumbnail
        )


def run_interactive_session(fmt_opt: Optional[str] = None, output_dir: Optional[str] = None, limit: int = 5):
    """Run the main interactive CLI session with seamless back navigation."""
    print_header()

    ffmpeg_ok, ffmpeg_path = check_ffmpeg()
    if not ffmpeg_ok:
        print_warning("ffmpeg binary was not found on system PATH.")
        print_info("Note: Single pre-merged video/audio streams will be downloaded automatically.\n")

    config = load_config()
    target_output = output_dir or config.get("download_dir", "./downloads")

    state = "SELECT_FORMAT" if not fmt_opt else "ENTER_QUERY"
    chosen_format = fmt_opt or config.get("default_format", "mp3")
    results = []

    while True:
        if state == "SELECT_FORMAT":
            chosen_format = prompt_format_selection(default_fmt=chosen_format)
            state = "ENTER_QUERY"

        elif state == "ENTER_QUERY":
            raw_prompt = prompt_search_query()
            if raw_prompt == "BACK":
                state = "SELECT_FORMAT"
                continue

            if is_playlist_url(raw_prompt):
                ret = execute_playlist_download(raw_prompt, chosen_format, target_output, ffmpeg_path)
                if ret in ["BACK_SEARCH", "BACK_FORMAT"]:
                    state = "ENTER_QUERY" if ret == "BACK_SEARCH" else "SELECT_FORMAT"
                    continue
                break

            refined = refine_query(raw_prompt, current_format=chosen_format)
            display_ai_refinement(refined.explanation, refined.cleaned_query, refined.suggested_format)
            final_format = refined.suggested_format

            with console.status("[bold cyan]Searching YouTube...[/bold cyan]", spinner="dots"):
                results = search_youtube(refined.cleaned_query, limit=limit)

            if not results:
                print_error("No YouTube results found. Try adjusting your search prompt.")
                state = "ENTER_QUERY"
                continue

            state = "SELECT_RESULTS"

        elif state == "SELECT_RESULTS":
            display_search_results_table(results)
            selected_items = prompt_select_video(results)

            if selected_items == "BACK_SEARCH":
                state = "ENTER_QUERY"
                continue
            elif selected_items == "BACK_FORMAT":
                state = "SELECT_FORMAT"
                continue

            execute_batch_download(selected_items, chosen_format, target_output, ffmpeg_path)
            break


def main():
    cli(obj={})


if __name__ == "__main__":
    main()
