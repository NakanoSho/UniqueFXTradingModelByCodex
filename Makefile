.PHONY: spot_pipeline forward_pipeline rates_pipeline vol_pipeline cost_pipeline macro_pipeline daily_report repro_spot bars_daily regime_daily scores_daily derived_daily

CONFIG ?= configs/v1_0.yaml

spot_pipeline:
	python -m data_pipeline.pipeline.run_spot_daily --input $(INPUT) --db $(DB) --source $(SOURCE) --log $(LOG) --config $(CONFIG)

forward_pipeline:
	python -m data_pipeline.pipeline.run_forward_daily --input $(INPUT) --db $(DB) --source $(SOURCE) --log $(LOG)

rates_pipeline:
	python -m data_pipeline.pipeline.run_rates_daily --input $(INPUT) --db $(DB) --source $(SOURCE) --log $(LOG)

vol_pipeline:
	python -m data_pipeline.pipeline.run_vol_daily --spot-db $(SPOT_DB) --db $(DB) --ts $(TS) --source $(SOURCE) --log $(LOG)

cost_pipeline:
	python -m data_pipeline.pipeline.run_expected_cost_daily --input $(INPUT) --db $(DB) --source $(SOURCE) --log $(LOG) --config $(CONFIG)

macro_pipeline:
	python -m data_pipeline.pipeline.run_macro_daily --input $(INPUT) --db $(DB) --source $(SOURCE) --log $(LOG)

daily_report:
	python -m ops.alerts.daily_report --metrics $(METRICS) --report $(REPORT)

repro_spot:
	python -m ops.repro.spot_repro --input $(INPUT) --db1 $(DB1) --db2 $(DB2) --source $(SOURCE) --log $(LOG) --config $(CONFIG)

bars_daily:
	python -m data_pipeline.pipeline.run_bars_daily --input $(INPUT) --output $(OUTPUT) --date $(DATE) --log $(LOG) --config $(CONFIG)

regime_daily:
	python -m data_pipeline.pipeline.run_regime_daily --output $(OUTPUT) --date $(DATE) --log $(LOG) --config $(CONFIG)

scores_daily:
	python -m data_pipeline.pipeline.run_scores_daily --forward-db $(FWD_DB) --output $(OUTPUT) --date $(DATE) --log $(LOG) --config $(CONFIG)

derived_daily:
	python -m data_pipeline.pipeline.run_derived_daily --input $(INPUT) --output $(OUTPUT) --forward-db $(FWD_DB) --date $(DATE) --config $(CONFIG) --log-dir $(LOG_DIR)
