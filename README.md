# Pete's TRMNL plugins

## Ceefax Football

Working Full landscape markup, men's results feed (including Championship), and server installation instructions are in football/. Polling URL: https://salsbury.uk/trmnl/football.php?device=YOUR_UNIQUE_INSTALLATION_ID

Each installation cycles independently through recent results. See football/INSTALL_LAYOUTS.md for URL configuration and revised page-counter markup.

The feed refreshes every 15 minutes. No API key is required. BBC Sport is the upstream source; its unofficial page structure may change. Revised shared markup and all four layouts are included. Follow football/INSTALL_LAYOUTS.md; Shared must be installed before the four layout render calls. TRMNL visual preview and Chef review are still required. Suggested tagline: Latest men's football results. Paste football/form-fields.yml into TRMNL Form Fields for the author description.

## Concept2 rowing

Awaiting the export of the working private plugin. Its exact source is not yet backed up here. Never commit Concept2 credentials or tokens.
