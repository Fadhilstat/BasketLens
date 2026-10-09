# BasketLens M5.5: approved research-evidence UI

This milestone implements the user-approved screenshot of the Data quality & methodology view in the existing Streamlit frontend. It is not a replacement HTML illustration and does not alter the analysis.

## Visual decisions

- Preserve the BasketLens forest-green research visual identity and non-promotional copy.
- Add document, checkmark, exclusion and shield pictograms exclusively to the existing four native data-quality metrics. All figures come from the unchanged quality manifest.
- Preserve the semantic five-step ordered validation list. Add numbered chips, meaning-specific icons and visible progression between steps on desktop, converting to vertical stages on small screens.
- Increase table readability through a quiet green header, alternating rows, right-aligned counts, tabular numerals and restrained emphasis of the final eligible-source-line row.
- Preserve accessible native tabs and explicitly show all four as two rows on mobile widths <= 480px. Keep keyboard focus and reduced-motion support.
- Retain existing dashboard, filters, country breakdown, real charts, basket builder, network explorer, exports, annotations and study caveats.
- Use only inline CSS icons with no external fonts or network dependency.

## Verification

The previously prepared M5.5 local preview passed 9 style checks and Chrome breakpoints at 1440/1024/390/320px. This preview is not the actual Streamlit rendering. The new release CI gate checks the genuine Streamlit runtime KPI icons, 5 semantic steps, numeric ledger alignment and mobile tab layout, in both full UCI and aggregate public mode. Model output and public exhibit parity remain mandatory.

## Release scope

Frontend CSS plus browser QA, automated design contract tests and continuity docs. No Python analytics, UCI workbook, raw user data, cryptographic manifest, Streamlit secrets or VPS deployment is changed.
