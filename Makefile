.PHONY: spot_pipeline forward_pipeline rates_pipeline vol_pipeline cost_pipeline macro_pipeline daily_report

spot_pipeline:
	python -m data_pipeline.pipeline.run_spot_daily --input $(INPUT) --db $(DB) --source $(SOURCE) --log $(LOG)

forward_pipeline:
	python -m data_pipeline.pipeline.run_forward_daily --input $(INPUT) --db $(DB) --source $(SOURCE) --log $(LOG)

rates_pipeline:
	python -m data_pipeline.pipeline.run_rates_daily --input $(INPUT) --db $(DB) --source $(SOURCE) --log $(LOG)

vol_pipeline:
	python -m data_pipeline.pipeline.run_vol_daily --spot-db $(SPOT_DB) --db $(DB) --ts $(TS) --source $(SOURCE) --log $(LOG)

cost_pipeline:
	python -m data_pipeline.pipeline.run_expected_cost_daily --input $(INPUT) --db $(DB) --source $(SOURCE) --log $(LOG)

macro_pipeline:
	python -m data_pipeline.pipeline.run_macro_daily --input $(INPUT) --db $(DB) --source $(SOURCE) --log $(LOG)

daily_report:
	python -m ops.alerts.daily_report --metrics $(METRICS) --output $(OUTPUT)
