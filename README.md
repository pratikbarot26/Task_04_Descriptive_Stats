# 🧪 Syracuse University iSchool OPT Research Task 04
## Descriptive Statistics of Social Media Activity with and without 3rd Party Libraries

This project explores and benchmarks three distinct approaches to compute descriptive statistics on large social media datasets from Facebook and Twitter, collected during the 2024 U.S. presidential election.

The goal is to produce identical statistical summaries using:
1. Pure Python (without third-party libraries)
2. Pandas (Python’s standard data analysis library)
3. Polars (a fast, modern DataFrame library written in Rust)

---

### 🧰 Getting Started

#### 💻 Prerequisites
Install the required libraries using pip:

`pip install numpy pandas polars pyarrow matplotlib seaborn`

#### 📁 Project Structure

```
/ (root)
├── Scripts/
│   ├── pure_python_fb_ads.py
│   ├── pure_python_fb_posts.py
│   ├── pure_python_tw_posts.py
│   ├── pandas_fb_ads.py
│   ├── pandas_fb_posts.py
│   ├── pandas_tw_posts.py
│   ├── polars_fb_ads.py
│   ├── polars_fb_posts.py
│   ├── polars_tw_posts.py
│   ├── viz_fb_ads.py
│   ├── viz_fb_posts.py
│   └── viz_tw_posts.py
├── Datasets/                  # 📦 Contains the input CSV datasets (not committed to repo)
├── Outputs/                   # 📄 Contains .txt summary outputs from the descriptive scripts
│   ├── pure_python_output_*.txt
│   ├── pandas_output_*.txt
│   └── polars_output_*.txt
├── Plots/
│   ├── plots_fb_ads/          # 📊 PNG plots from visualization scripts
│   ├── plots_fb_posts/
│   └── plots_tw_posts/
└── README.md
```

#### 🧾 What Each Script Produces

1. Pure Python / Pandas / Polars scripts
   
    ✅ Write structured .txt files with:

    - Overall and grouped descriptive statistics
    - Clear formatting of numeric, categorical, and binary column summaries
    - Runtime performance logs (in seconds)

2. Visualization scripts (viz_*.py)
    🖼 Generate .png charts based on:
   
    - Frequency distributions
    - Time trends
    - Engagement metrics
      
    (Plots are saved inside corresponding plots_* folders)

#### Sample outputs and visualizations are stored in the outputs folders. The .txt outputs from fb_ads dataset are not included as they were huge in size.

💡 Note: Datasets are required to be placed inside the Datasets/ folder locally. These are not committed to the repository for size and compliance reasons. Instructions for downloading datasets are included in the README.

---

### 📥 Dataset Access

#### ⚠️ Data files are not included in this repository for size and compliance reasons.

To replicate results, you will need datasets that resemble the following schema:

`2024_fb_ads_president_scored_anon.csv`

`2024_fb_posts_president_scored_anon.csv`

`2024_tw_posts_president_scored_anon.csv`

These datasets relate to political advertising and social media engagement during the 2024 U.S. Presidential election, and include variables for engagement, content themes, and audience targeting.

#### 🔎 Suggested Data Sources

While the original datasets were sourced via academic access and are no longer publicly available, similar datasets might be accessible through:

 - Meta Ad Library API – for Facebook political ads metadata

 - Twitter Transparency Center (Archive) – legacy political ad data prior to platform policy shifts

 - Social Science One – academic research access to Facebook and Instagram data

 - ICPSR (Inter-university Consortium for Political and Social Research)

 - GDELT Project – global event and media tracking with social indicators

 - Harvard Dataverse

 - Stanford Internet Observatory – research on influence campaigns

 - Academic partnerships or institutional datasets (available via request)

#### 🗂 Folder Setup

To run the scripts:

Place your datasets inside the local /Datasets/ folder.

Use filenames that match or map to the above examples.

Ensure the CSV schema matches the columns expected by the scripts.
Mismatched or renamed columns will lead to runtime errors or incomplete summaries.

#### 👉 Tip: Open any script and inspect the NUMERIC_COLS, CATEGORICAL_COLS, and BINARY_COLS lists to validate compatibility.

---

### 📊 What Each Script Computes
Each script (across Pure Python, Pandas, and Polars) computes descriptive statistics in a structured format. Despite differences in implementation, the outputs are functionally identical, thanks to aligned logic and preprocessing.

- Numeric Summary

  - Metrics: count, nulls, mean, std, min, 25%, 50%, 75%, max

  - Applied only to true numeric columns (e.g., likeCount, viewCount)

- Categorical Summary

  - Fields: unique count, most frequent value, frequency count of top 5 values

  - Handles ID strings, labels, and dates

- Binary Summary

  - Computed as count of 1s and 0s

  - Only in the Pure Python implementation (excluded from Pandas & Polars for parity)

- Grouped Analysis

  - Facebook ads dataset: grouped by page_id, then (page_id, bylines, currency)
 
  - Facebook posts dataset: grouped by page_id then (page_id, page_category)

  - Twitter dataset: grouped by source, then (source, lang)

#### These columns were chosen for aggregation as they were non-unique categorical columns which made sense to be aggregated on. The given column ad_id was a unique column and hence was a redundant aggregation candidate in my opinion.

Additional care was taken to:

 - Handle missing/nulls consistently across frameworks

 - Avoid analyzing dummy/binary columns as continuous variables

 - Manually cast columns to correct types where auto-detection failed

 - Format floating-point output consistently across Pandas and Polars (disable scientific notation, apply rounding)

 - Together, these ensure identical summaries across all frameworks while staying true to each tool's native conventions.

---

### ⏱️ Performance Comparison
Each script includes a runtime timer. Here are the final results:

| Script				|Runtime (seconds) |
|---------------|------------------|
| pure_python_fb_posts	|0.63      |
| pure_python_fb_ads	  |83.06     |
| pure_python_tw_posts	|1.26      |
| pandas_fb_posts		    |1.29      |
| pandas_fb_ads			    |309.64    |
| pandas_tw_posts		    |0.75      |
| polars_fb_posts		    |1.51      |
| polars_fb_ads			    |317.55    |
| polars_tw_posts		    |0.60      |


### 🔍 Observations

- Polars was expected to outperform Pandas, but that wasn't always the case; especially with the facebook_ads dataset.

- Pandas outperformed Polars on the largest file (fb_ads), possibly due to better internal optimization for high-cardinality categorical columns and flexible groupings.

- Pure Python was fastest, but only because its analysis is shallow (no percentiles, no full group summaries).

- Polars was fastest for the Twitter dataset, likely due to simpler grouping and lighter memory overhead.

---

### 🤖 AI-Assistance Reflection
AI tools like ChatGPT, Gemini, etc. can play a major role in helping structure and accelerate coding endeavors like this research project. But while the initial push was strong, maintaining consistency, performance, and data accuracy still required human expertise.

<br>

#### ✅ What AI Did Well

- Kickstarted the entire codebase: AI tools helped produce baseline scripts for all three frameworks - Pure Python, Pandas, and Polars, in a fraction of the time it would take manually.

- Enforced logical consistency: AI templates made it easy to apply a common summary structure (numeric, categorical, binary, grouped) across different libraries.

- Accelerated iterations: Need a .groupby() logic, a .describe() workaround, or a quick fix for nulls? AI served up useful snippets rapidly, streamlining development.

- Performance logging and formatting: Even the timer-based runtime logging and helper functions like Tee for writing and printing were AI-generated and then refined for usability.

<br>


#### ⚠️ Where AI Fell Short

Despite its strengths, AI-generated code is not ready for production without human validation. Key gaps I encountered:

- Misunderstood data types: AI repeatedly treated illuminating_scored_message as numeric, when it’s actually categorical. Similarly, it missed distinctions between dummy columns (binary flags) and actual values.

- Fabricated columns: Suggestions included non-existent columns like "Page Name" or "verified" which caused immediate crashes if copied directly.

- Overgeneralized templates: Polars code often reused Pandas-style syntax, leading to issues like .groupby() being called instead of .group_by() or trying to sort nonexistent "counts" columns.

- No data validation: AI didn’t cross-check output consistency between frameworks. I had to manually verify every .txt output to ensure parity across Pure Python, Pandas, and Polars.

- Lacked formatting precision: Scripts often defaulted to scientific notation, truncated strings, or improperly sorted outputs - all of which had to be fixed manually for clean reporting.

<br>

#### 🧠 Common AI Patterns Observed

- Pandas bias: Nearly every descriptive statistics example started with Pandas. It’s an excellent first choice, but AI rarely considers the performance or memory tradeoffs that make Polars better for large datasets.

- Assumes perfect data: Many snippets lacked checks for missing values, inconsistent types, or string cleaning which are all critical in real-world datasets.

- Minimal error-proofing: AI doesn’t know what it doesn’t know; so unless prompted very specifically, it’ll assume things like .groupby() will always succeed or that all columns are present in every dataset.

- No context carry-over between approaches: While ChatGPT and Copilot could generate templates for each framework, it didn’t cross-validate them for identical output structure unless we asked explicitly.

<br>

#### 💬 Final Verdict

#### `AI can get us 70% of the way there  but the last 30% requires human insight, debugging, and patience.`


AI can absolutely jumpstart data analysis projects. It’s a powerful productivity tool for:

- Prototyping reusable code

- Exploring syntax in unfamiliar libraries

- Quickly iterating when you’re stuck

But if you’re:

- Comparing outputs across multiple frameworks,

- Handling real-world dirty data,

- Or targeting professional, reproducible results...

...you’ll need human intuition and rigorous validation.

---

### 🙋‍♂️ Advice for Junior Analysts
Start with AI when building your project skeleton. Let it help you structure your logic, initialize your scripts, and explain unknown methods. But do not rely on it blindly - you are responsible for:

- Understanding the schema of your dataset

- Adjusting logic for edge cases

- Validating the quality and consistency of outputs.

That last part, validation, is where analysts grow from script users to data storytellers.

| Situation								              | Recommended Tool        |
|---------------------------------------|-------------------------|
| Learning descriptive stats			      |    Pure Python          |
| Day-to-day analysis & exploration		  |    Pandas               |
| Memory-efficient processing at scale	|    Polars (with care)   |
| Need for rich visualizations		    	|    Pandas + Seaborn     |
| Interpreting categorical data			    |    Pandas               |

---

### 📊 Bonus Visualizations

The following scripts generate helpful visual summaries:

` viz_fb_ads.py `

` viz_fb_posts.py `

` viz_tw_posts.py `

They include:

- Top-performing posts/pages

- Histograms and boxplots of engagement

- Time-distribution of content creation

These are great tools for presenting insights and validating summaries visually.

---

### ✅ Final Thoughts

This task was a deep dive into descriptive statistics, benchmarking, and consistency across frameworks.

It helped sharpen:

- Data engineering and cleaning

- Formatting and report generation

- Comparative performance analysis

### 🎯 The final output is a set of reliable, reusable summary scripts with the flexibility to plug into any campaign dataset in the future.
