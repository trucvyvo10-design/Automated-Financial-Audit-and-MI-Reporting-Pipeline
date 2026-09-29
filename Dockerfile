FROM python:3.10-slim

WORKDIR /app

# Copy requirement file
COPY 04_Python_Automation/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose Streamlit port
EXPOSE 8501

WORKDIR /app/04_Python_Automation

CMD ["python3", "-m", "streamlit", "run", "app_risk_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
