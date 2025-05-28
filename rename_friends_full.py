import os
import re
import glob
import readline
from datetime import datetime

# --- Autocomplete Setup ---
def complete_path(text, state):
    line = readline.get_line_buffer()
    expanded = os.path.expanduser(line)
    matches = glob.glob(expanded + '*')
    return matches[state] if state < len(matches) else None

readline.set_completer_delims(' \t\n;')
readline.set_completer(complete_path)
readline.parse_and_bind('tab: complete')

# --- Load Rename Map ---
def load_rename_map(map_file):
    structured_map = {}
    pattern = re.compile(r"^(S\d{2}E\d{2,3})-(Friends_Season_\d+_Disc_\d+_t\d+\.mkv)")

    with open(map_file, "r", encoding="utf-8") as f:
        for line in f:
            match = pattern.match(line.strip())
            if match:
                episode, original = match.groups()
                new_name = f"Friends {episode}.mkv"
                season_disc = re.search(r"Season_(\d+)_Disc_(\d+)", original)
                if season_disc:
                    season, disc = season_disc.groups()
                    season_key = f"S{int(season):02d}"
                    disc_key = f"D{int(disc)}"
                    structured_map.setdefault(season_key, {}).setdefault(disc_key, {})[original] = new_name
    return structured_map

# --- Main Program ---
def main():
    print("📺 Friends Renamer Utility\n")

    folder = input(
        "📁 Enter the full path to the folder containing the video files:\n"
        "(e.g., /home/yourname/Videos/Friends/S02D2)\n> "
    ).strip()

    if not os.path.isdir(folder):
        print(f"\n❌ That directory doesn’t exist:\n{folder}")
        return

    season = input("📦 Enter the season number (e.g., 2): ").strip().zfill(2)
    season_key = f"S{season}"

    structured_map = load_rename_map("friends_map.txt")

    if season_key not in structured_map:
        print(f"\n❌ Season {season} is not in the mapping.")
        return

    # Show available discs with episode ranges
    print(f"\n💿 Available discs for Season {season}:")
    for disc_key in sorted(structured_map[season_key].keys()):
        files = structured_map[season_key][disc_key]
        eps = [re.search(r'S\d{2}E(\d{2,3})', new).group(1) for new in files.values()]
        eps_range = f"Episodes {min(eps)}–{max(eps)}" if eps else "No episodes"
        print(f"  - Disc {disc_key[-1]}: {eps_range}")

    disc = input("\n📥 Enter the disc number from the list above (just the number): ").strip()
    disc_key = f"D{disc}"

    if disc_key not in structured_map[season_key]:
        print(f"\n❌ Disc {disc} is not valid for Season {season}.")
        return

    rename_map = structured_map[season_key][disc_key]
    renamed = set()

    log_path = os.path.join(folder, "rename_log.txt")
    with open(log_path, "w", encoding="utf-8") as log:
        log.write(f"Rename Log - {datetime.now()}\n")
        log.write(f"Season: {season_key}, Disc: {disc_key}\n\n")

        for old, new in rename_map.items():
            old_path = os.path.join(folder, old)
            new_path = os.path.join(folder, new)
            if os.path.exists(old_path):
                print(f"Renaming: {old} ➜ {new}")
                os.rename(old_path, new_path)
                renamed.add(new)
                log.write(f"✅ Renamed: {old} ➜ {new}\n")
            else:
                print(f"⚠️ File not found: {old}")
                log.write(f"⚠️ Missing: {old}\n")

    print(f"\n✅ Done! Log saved to: {log_path}")

# Run it
if __name__ == "__main__":
    main()
