### The Problem Statement / Use Case

**The Scenario:**
You work as a Data Engineer for a regional coffee shop chain that has outdoor patios. The store managers are struggling with **staffing and inventory optimization**.

- On sunny days, they run out of iced coffee and the patio is packed (understaffed).
- On rainy or freezing days, foot traffic dies, and staff are sitting around doing nothing (wasting money).

**The Goal:**
The Data Analytics team wants to build a predictive model to forecast daily sales and optimize employee schedules based on the weather. However, they currently have no historical weather data.

Your job is to build the data pipeline that captures daily weather data and stores it in a clean, queryable database so the Data Analysts can later join it with their daily sales data.

### The Business Questions Your Data Will Answer

Once your pipeline has been running for a few months, analysts will use your database to answer:

1. _How much does a drop in temperature below 50°F affect total foot traffic?_
2. _Does rain reduce total sales, or just shift sales from iced drinks to hot drinks?_
3. _If wind speeds exceed 15 mph, do we see a drop in outdoor patio seating utilization?_
