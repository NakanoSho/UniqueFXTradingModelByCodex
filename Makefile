.PHONY: spot_pipeline forward_pipeline rates_pipeline vol_pipeline expected_cost_pipeline metrics_collect daily_report vol_metrics_pipeline

spot_pipeline:
	python -m data_pipeline.pipeline.run_spot_daily --input $(INPUT) --db $(DB) --source $(SOURCE) --log $(LOG)

forward_pipeline:
	python -m data_pipeline.pipeline.run_forward_daily --input $(INPUT) --db $(DB) --source $(SOURCE) --log $(LOG)

rates_pipeline:
	python -m data_pipeline.pipeline.run_rates_daily --input $(INPUT) --db $(DB) --source $(SOURCE) --log $(LOG)

vol_pipeline:
	python -m data_pipeline.pipeline.run_vol_daily --spot-db $(SPOT_DB) --db $(DB) --ts $(TS) --source $(SOURCE) --log $(LOG)

vol_metrics_pipeline:
	python -m data_pipeline.pipeline.run_vol_metrics_daily --spot-db $(SPOT_DB) --db $(DB) --ts $(TS) --source $(SOURCE) --log $(LOG)

expected_cost_pipeline:
	python -m data_pipeline.pipeline.run_expected_cost_daily --input $(INPUT) --db $(DB) --source $(SOURCE) --log $(LOG)

metrics_collect:
	python -m ops.alerts.collect_metrics --inputs $(INPUTS) --output $(OUTPUT)

daily_report:
	python -m ops.alerts.daily_report --metrics $(METRICS) --report $(REPORT)
