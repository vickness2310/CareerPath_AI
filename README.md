CareerPath AI 🧭 (📋 Assignment Project)

AI-Powered Career Recommendation System for Malaysian Students

📌 About The Project

CareerPath AI is a five-page interactive web-based career recommendation system developed specifically for Malaysian students who are struggling to choose the right career path after completing their SPM, STPM, or Diploma. Many students in Malaysia face this challenge without proper guidance, often ending up in courses that do not match their interests or strengths. This project was built to solve that problem by providing a data-driven, personalised career recommendation in just 3 minutes.

💡 Why I Built This

As a student ourselves, I noticed that most career guidance tools available online are either too generic, not tailored for the Malaysian education system, or do not provide financial information such as university fees and PTPTN loan details. CareerPath AI was built to fill that gap by combining real datasets, AI-powered matching, and Malaysian-specific financial data all in one platform.

⚙️ How It Works

User fills in their personal profile including income category (B40/M40/T20)

User selects their interests from 12 categories and adjusts preference sliders

A points-based algorithm scores every career based on the user's answers

The career with the highest score is recommended

The system pulls real salary data, universities and PTPTN info from Kaggle datasets

Results are displayed with full financial breakdown per university

🗂️ Datasets Used (from Kaggle)

Dataset	Source	Records
Salary Data: 	mohithsairamreddy/salary-data	6,699 records
World Universities: 	thedevastator	9,000+ universities (148 Malaysian)
Career Recommender: 	Kaggle	1,195 student survey responses


🛠️ Tools & Technologies

Tool	Purpose
HTML / CSS / JavaScript	Frontend website — all 5 pages

Python 3	Data processing and local server

Pandas Library	Read and process Kaggle CSV datasets

JSON	Bridge between Python data and website

Canvas API	Animated particle network background

CSS Animations	Robot character, page transitions, glowing effects

VS Code	Code editor

Python HTTP Server	Run website locally via localhost:8000

🚧 Challenges & How We Solved Them

Challenge 1 — Kaggle salary data was in USD
The original Kaggle salary dataset used USD values which gave unrealistic results like RM 19,000 starting salary for a Software Engineer. We solved this by replacing the salary data with real Malaysian market rates researched from Jobstreet and MyFutureJobs.

Challenge 2 — Cannot open HTML file directly
When opening the HTML file by double clicking, the browser blocked the JSON data from loading due to CORS security restrictions. We solved this by running a Python local HTTP server using python -m http.server 8000 which allows the website to fetch the JSON file properly.

Challenge 3 — PTPTN coverage was the same for all universities
Initially the system showed the same PTPTN amount for every university regardless of whether it was public or private. We solved this by implementing a proper PTPTN rate matrix based on official PTPTN policy — B40, M40 and T20 categories each with different coverage rates for public and private universities.

Challenge 4 — Robot animation not triggering on Page 5
The robot character was not updating to the celebrate animation on the results page because Page 5 loads automatically without a button click. We solved this by implementing a setInterval function that checks every 500ms which page is currently active and updates the robot accordingly.

📊 Key Features

✅ 5-page smooth animated website

✅ Points-based AI career matching algorithm

✅ Real salary data from 6,699 Kaggle records

✅ 148 real Malaysian universities from Kaggle dataset

✅ PTPTN calculator based on B40/M40/T20 income category

✅ Individual PTPTN breakdown per university (Public vs Private)

✅ Animated robot character with different reactions per page

✅ Particle network canvas background

✅ ETL pipeline — CSV → Python → JSON → Website

