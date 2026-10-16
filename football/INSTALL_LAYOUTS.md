# Install football results cycling

Polling URL for Pete's installation:
https://salsbury.uk/trmnl/football.php?device=pete-trmnl

Use a different device value for every independent installation, e.g. kitchen-trmnl or office-trmnl. Allowed characters: letters, numbers, underscore, hyphen (1–128 characters). These are public labels, not passwords. Installations sharing the same value share their place in the cycle. TRMNL polling identifies the installation, not the physical hardware automatically.

Keep GET polling every 15 minutes, with no extra headers or body. For Half horizontal or Quadrant use:
https://salsbury.uk/trmnl/football.php?device=pete-trmnl&rows=6

Full and Half vertical can use the default 14 rows. If one installation is used with multiple layout sizes, use rows=6 so compact displays do not omit matches.

Paste shared.liquid into Shared, then full.liquid, half_horizontal.liquid, half_vertical.liquid and quadrant.liquid into the matching tabs. Save. All four render calls pass page_label to the Shared template.

Each poll advances one page, wrapping at the end. Requests repeated within 30 seconds return the same page to protect against immediate retries. HEAD requests do not advance. New or corrected results restart at page 1; timestamp-only updates do not. The server paginates all matches retained in football.json, with a repeated competition/date heading on each page. The generator searches back up to 30 days and retains every eligible completed result from the first date with matches. There is no total match cap and no topping up from older dates.

The old football.json URL remains available as the static first-page feed. Changing only markup will not enable cycling: update the polling URL too.

Server: install football.php alongside football.json at /var/www/salsbury.uk/trmnl/football.php. Requires Apache PHP with PDO SQLite. Create private state directory:
```sh
install -d -o www-data -g www-data -m 750 /var/lib/trmnl-football
```
State contains hashed installation labels and progress, not IP addresses. Unused entries expire after 90 days on subsequent requests. The response is marked no-store. No Apache restart is required on this host.

Verification: PHP syntax and live HTTPS requests tested for independent IDs, retry protection, full wraparound without missing matches, and compact row limits. Visual preview in TRMNL is still required after pasting markup.
