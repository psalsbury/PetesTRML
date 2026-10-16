# Football page sizing

The PHP endpoint defaults to six text rows per page, including repeated competition headings. This avoids sending twelve matches to an OG view that clips the bottom rows. The default applies when the polling URL has no rows parameter. Existing explicit rows parameters override it; use rows=6 for the current Full layout. The latest match day is preserved; all results from that day are paginated.

Polling URL: https://salsbury.uk/trmnl/football.php?device={{ trmnl.device.friendly_id }}

Each installation cycles independently. The response includes page_number, page_count, page_label, total_count and row_budget. The Full layout should pass page_label into the shared template's pagination argument.

Verification on 16 October 2026: all 36 stored results from 15 October returned exactly once over eight default pages, each at most six rows, followed by wrap to 1/8. This checks feed coverage; preview smaller mashup layouts with their corresponding row budgets separately.
