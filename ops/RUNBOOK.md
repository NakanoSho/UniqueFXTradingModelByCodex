# Operations Runbook (MVP)

## Daily
- Run spot pipeline (ingest -> normalize -> QC -> store)
- Generate daily monitoring report
- Check alerts and log any breaches

## Weekly
- Review data quality flags
- Review execution cost drift (Real vs Expected)

## Incident Handling
- If DD or loss limits are hit, follow kill-switch protocol in design doc
- If data anomalies persist, halt trading signals and investigate data pipeline
