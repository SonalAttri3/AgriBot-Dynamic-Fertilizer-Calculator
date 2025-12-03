🌱 AgriBot - Dynamic Fertilizer Calculator

AgriBot is a conversational AI assistant built with Streamlit and Python. It helps farmers and agricultural planners calculate the optimal amount of nitrogen fertilizer (Urea) required for their crops based on specific district-level soil health data.

🚀 Features

Chat Interface: Natural language interaction (e.g., "Plan for Rice in Ludhiana").

Dynamic Calculation: Automatically calculates excess soil nitrogen and potential Urea reduction.

Smart Parsing: Detects district, state, and crop names from user messages.

Custom Data: Allows users to upload their own CSV datasets via the sidebar.

Error Handling: Robust handling of missing data or incorrect file formats.

📂 Project Structure

AgriBot/
├── agribot.py           # Main application code
├── requirements.txt     # List of Python dependencies
├── README.md            # Project documentation
├── C1.csv               # (Default) Crop nutrient requirements
└── Fdistrict.csv        # (Default) District-level soil data


🛠️ Installation & Setup

1. Prerequisites

Python 3.8 or higher installed.

2. Install Dependencies

Open your terminal or command prompt in the project folder and run:

pip install -r requirements.txt


(Note: On Mac/Linux, you might need to use pip3 instead of pip)

▶️ How to Run

Run the application using Streamlit:

streamlit run agribot.py


(Note: On Mac/Linux, use python3 -m streamlit run agribot.py if the above command fails)

The application will open automatically in your default web browser at http://localhost:8501.

📊 Data Format

If you want to upload your own data, ensure your CSV files follow this structure:

1. Crop Requirements (C1.csv)

Row 1: Header descriptions (ignored by the bot)

Row 2: Column Headers

Columns Required: crop, N(kg/ha)

Example:

Standard crop nutrient requirement,,,,
crop, N(kg/ha), P, K
wheat, 120-150, 60, 40
rice, 100-120, 60, 40


2. District Soil Data (Fdistrict.csv)

Row 1: Header descriptions (ignored by the bot)

Row 2: Column Headers

Columns Required: district, state, Avg. soil N(kg/ha)

Example:

District level soil status,,,,
state, district, Avg. soil N(kg/ha)
punjab, ludhiana, 245
haryana, hisar, 215


🧩 Troubleshooting

"Command not found": Ensure you have installed Python and added it to your system PATH.

"KeyError" or "Column not found": Check your CSV files. The bot expects the headers to be on the second row (row index 1). If your headers are on the first row, you will need to edit skiprows=1 to skiprows=0 in agribot.py.

App Stuck/Old Data: Use the "🔄 Reset / Clear Cache" button in the sidebar to refresh the application.

📜 License

This project is open-source and available for educational and agricultural planning purposes.