@echo off
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate
echo Installing packages...
pip install --upgrade pip
pip install Flask==3.0.0 Werkzeug==3.0.1 ollama Pillow python-dotenv
echo Done! Now run: python app.py
pause