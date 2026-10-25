# TRMNL football results

Men's completed results from BBC Sport, displayed in a monochrome Ceefax layout.

Install football/update_trmnl_football.py at /var/www/salsbury.uk/tools/update_trmnl_football.py and run with Python 3. Requires zoneinfo system time zone data and no third-party packages.

Cron (/etc/cron.d/trmnl-football):
```
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
*/15 * * * * root /usr/bin/python3 /var/www/salsbury.uk/tools/update_trmnl_football.py > /var/www/salsbury.uk/.trmnl-football-cache/update.log 2>&1
```

Create the cache folder before cron runs. Run the script once to generate football.json. Results are ordered by kickoff time, newest first. The static first page includes at most 12 matches and 14 table rows including headings. The paginated endpoint cycles through every match from the most recent UK date with eligible completed results, without a minimum count, a 60-match cap, or topping up from older dates. The feed keeps saved results on upstream failure and displays a warning. BBC page structure is an unofficial data dependency and may change.

TRMNL: create a new private plugin, Polling, GET https://salsbury.uk/trmnl/football.php?device=YOUR_UNIQUE_INSTALLATION_ID, no headers or body, refresh every 15 minutes. Follow INSTALL_LAYOUTS.md: paste shared.liquid into Shared, then each of the four layout files into its corresponding tab. Full markup requires the Shared template. Use landscape orientation. Add to playlist. Existing rowing plugin is separate.

For independent page cycling, server setup, compact layouts and retry behaviour see [INSTALL_LAYOUTS.md](INSTALL_LAYOUTS.md). The static JSON URL remains supported.

## Where each file lives on the server

This repository is the source for everything TRMNL football on salsbury.uk (moved out of PetesGames on 2026-10-25).

| Repo file | Live location |
|---|---|
| `football/update_trmnl_football.py` | `/var/www/salsbury.uk/tools/update_trmnl_football.py` (run by cron) |
| `football/deploy/cron.d/trmnl-football` | `/etc/cron.d/trmnl-football` (every 15 minutes) |
| `football/football.php` | `/var/www/salsbury.uk/trmnl/football.php` (paginated polling endpoint) |
| `football/football.liquid` | `/var/www/salsbury.uk/trmnl/football.liquid` (original single-page Full markup for the static `football.json` URL) |

Generated, never committed: `/var/www/salsbury.uk/trmnl/football.json` (written by the script) and `/var/www/salsbury.uk/.trmnl-football-cache/` (daily caches, lock, log). PetesGames deploys exclude `/trmnl/` and `/tools/update_trmnl_football.py`.
