# agentic-loan-approval-demo

By Janif Shaikh

- Live demo: [ https://janifsheikh7-beep.github.io/agentic-loan-approval-demo/ ]
- D5 Research note: D5.pdf ( https://drive.google.com/file/d/1Y51h1Qsrw9Ecwm7V2JIe9koddf3-7wkB/view?usp=sharing )
- D6 AI usage log: D6.pdf ( https://drive.google.com/file/d/1rKuzw6-vxbepkFEaacjufrKQ0HnHt8pT/view?usp=sharing )
- Screen recording: [ https://drive.google.com/file/d/17n4X5sCfFx9RWpt8fCWDfHG6Xxy0SgYs/view?usp=sharing ]

## What this is
A presales demo of an agentic AI loan approval journey for salaried personal loans.

## Honest scope
The demo runs on synthetic data simulated in the browser. The agent steps are scripted, not live LLM calls. `bigquery_setup.py` generates synthetic data and loads it into BigQuery, but the demo is not connected to it yet.

## Run locally
Open index.html in a browser.
For BigQuery: pip install faker pandas google-cloud-bigquery pandas-gbq
then python bigquery_setup.py
