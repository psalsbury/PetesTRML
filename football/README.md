# TRMNL football results

Men's completed results from BBC Sport, displayed in a monochrome Ceefax layout.

Install football/update_trmnl_football.py at /var/www/salsbury.uk/football/update_trmnl_football.py and run with Python 3. Requires zoneinfo system time zone data and no third-party packages.

Cron (/etc/cron.d/trmnl-football):
```
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
*/15 * * * * root /usr/bin/python3 /var/www/salsbury.uk/football/update_trmnl_football.py > /var/www/salsbury.uk/.trmnl-football-cache/update.log 2>&1
```

Create the cache folder before cron runs. Run the script once to generate football.json. Results are ordered by kickoff time, newest first. Output includes at most 12 matches and 14 table rows including headings. The feed keeps saved results on upstream failure and displays a warning. BBC page structure is an unofficial data dependency and may change.

TRMNL: create a new private plugin, Polling, GET https://salsbury.uk/trmnl/football.php?device=YOUR_UNIQUE_INSTALLATION_ID, no headers or body, refresh every 15 minutes. Follow INSTALL_LAYOUTS.md: paste shared.liquid into Shared, then each of the four layout files into its corresponding tab. Full markup requires the Shared template. Use landscape orientation. Add to playlist. Existing rowing plugin is separate.

For independent page cycling, server setup, compact layouts and retry behaviour see [INSTALL_LAYOUTS.md](INSTALL_LAYOUTS.md). The static JSON URL remains supported.
