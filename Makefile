.PHONY: spot_pipeline

spot_pipeline:
	python -m data_pipeline.pipeline.run_spot_daily --input $(INPUT) --db $(DB) --source $(SOURCE) --log $(LOG)
