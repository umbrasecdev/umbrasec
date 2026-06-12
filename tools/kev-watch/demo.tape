# vhs recording script for the kev-watch README demo GIF.
#
# vhs scripts a terminal recording so the GIF is reproducible - re-run this
# any time the output format changes instead of hand-recording.
#
# Install (vhs needs ttyd and ffmpeg on PATH):
#   https://github.com/charmbracelet/vhs#installation
#   e.g.  go install github.com/charmbracelet/vhs@latest
#
# Record from this directory:
#   cd tools/kev-watch && vhs demo.tape
#
# Before recording, refresh the --since date below to ~4 weeks back so the
# first beat shows current entries (it is a static query; it ages).

Output ../../assets/kev-watch-demo.gif

Set Shell "bash"
Set FontSize 15
Set Width 1000
Set Height 600
Set Padding 16
Set Theme "Catppuccin Mocha"
Set TypingSpeed 35ms

# Beat 1: the watchlist - actively exploited CVEs in the stack you run
Type "python3 kev_watch.py --watch fortinet ivanti citrix vmware --since 2026-05-15"
Sleep 600ms
Enter
Sleep 5s

# Beat 2: CISA remediation deadlines due within a week
Type "clear"
Enter
Sleep 300ms
Type "python3 kev_watch.py --due-soon 7"
Sleep 600ms
Enter
Sleep 6s
