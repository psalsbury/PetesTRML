# Install revised layouts

In TRMNL Edit Markup, paste shared.liquid into Shared, and paste the contents of full.liquid, half_horizontal.liquid, half_vertical.liquid and quadrant.liquid into the matching four tabs. Save all changes. The render calls depend on Shared and will not work alone.

Keep the existing polling URL and Form Fields. Set the plugin tagline/description to: Latest men's football results

Full and Half vertical show up to 14 feed rows including competition headings; Half horizontal and Quadrant show up to 6. Team names are shortened where necessary. The feed contains completed men's matches, including Championship. Source timestamps are shown in UK time. No personal credentials are stored in this repository.

Liquid content was checked using LiquidJS against live feed data, empty arrays and missing results. Browser visual validation and TRMNL Chef review remain to be performed in TRMNL. Custom CSS is scoped to petes-football to avoid affecting other mashup plugins. The original working Full layout is in archive/full-original.liquid.
