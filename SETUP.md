# Setup and Running Instructions

## Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

## Step 1: Install Dependencies

### Option A: Using pip (Recommended)
```bash
pip install -r requirements.txt
```

### Option B: Using a Virtual Environment (Recommended for isolation)
```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Step 3: Access the Website

Open your web browser and navigate to:
- **Homepage**: http://localhost:5000/
- **Companies Search**: http://localhost:5000/search.html
- **My Draft**: http://localhost:5000/my-draft.html
- **Friends**: http://localhost:5000/friends.html

## Troubleshooting

### If you get import errors:
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- If using a virtual environment, make sure it's activated

### If the port is already in use:
- The app runs on port 5000 by default
- You can change the port in `app.py` at the bottom: `app.run(debug=True, port=5000)`

### If companies don't load:
- The app fetches data from yfinance on startup, which may take a minute
- Check the terminal for any error messages
- Make sure you have an internet connection (yfinance needs to fetch stock data)

### If you see CORS errors:
- CORS is already enabled in the app, but if you still see errors, check that `flask-cors` is installed

## First Run Notes

- On first run, the app will fetch earnings data for all companies (this may take 30-60 seconds)
- A default user will be created automatically when you first add a company to your draft
- You start with $100 budget to draft companies
