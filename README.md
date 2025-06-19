# Tricky - A Skateboarding Trick Learning App
### Live Demo
Note: For demonstration purposes, the "Ollie" and "Kickflip" trick pages have been fully updated with proper video content. Every other trick page contains placeholder messages.

https://tricky.streamlit.app/
## About The Project
Tricky is an interactive web app for learning how to do skateboarding tricks and tracking your progress. I developed this project to deepen my understanding of full-stack development, practice applying HCI principles, and showcase my ability to build a complete, data-driven web solution. Tricky contains 145 tricks categorized by difficulty level and an intuitive UI that allows users to easily search for and filter tricks. It was designed to provide a comprehensive learning experience that involves curated video content with precise timestamp controls, similar trick suggestions, and personal progress tracking. It also features a data analytics dashboard for visualizing user progression metrics, category completion rates, and intelligent trick recommendations for skill advancement.

## Features

* Browse tricks by difficulty category (Beginner, Easy, Intermediate, Advanced, Expert)
* Filter tricks by type (Flip Tricks, Shove-Its & Spins, Ollie-Based Tricks, Other)
* Search for specific tricks
* View instructional videos for each trick (Slow Motion Demonstration, Pro Skater Examples, Tutorial Video)
* Precise start and end times for each video
* Video replay functionality (from the start time of the trick)
* Mark tricks as learned to track progression
* Similar trick suggestions for each trick
* Visual feedback of completed tricks on home page
* Data analytics dashboard for visualizing progression and viewing tailored trick recommendations
* Seamless page navigation with clear buttons

## Tech Stack
* Frontend:

  * Streamlit – A powerful open-source Python library used to create interactive web applications for data science and machine learning.
  * CSS – Used for custom styling and ensuring a polished user interface.
* Data Storage:

  * CSV Files (.csv) – For structured data storage, specifically to store all of the tricks and their difficulty ratings.
  * JSON Files (.json) – Used for flexible data storage, managing user progress (completed tricks) and storing detailed video metadata (including URLs, start/end times, and video categories).
* Data Analysis & Visualization:
  * Pandas – A robust Python library for data manipulation and analysis, crucial for processing trick data and user progression.
  * Plotly – A versatile Python graphing library used to create the interactive and insightful data analytics dashboard.
* Programming Language:

  * Python – The primary programming language powering the application's logic and data processing.
* Version Control:

  * Git – For managing project versions and facilitating development.
  * GitHub – Hosting the project repository and enabling collaboration.

