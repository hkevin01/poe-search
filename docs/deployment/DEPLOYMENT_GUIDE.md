# Deployment Guide

## Development Deployment

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd poe-search
   ```

2. **Setup Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate  # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements/base.txt
   ```

4. **Configure Tokens**
   ```bash
   cp config/environments/tokens.json.example config/environments/tokens.json
   # Edit tokens.json with your Poe.com tokens
   ```

5. **Run Application**
   ```bash
   python gui_launcher.py
   ```

## Production Deployment

### Docker Deployment

1. **Build Image**
   ```bash
   docker build -t poe-search .
   ```

2. **Run Container**
   ```bash
   docker run -p 8080:8080 poe-search
   ```

### System Service

Create systemd service for Linux deployment:

```ini
[Unit]
Description=Poe Search Service
After=network.target

[Service]
Type=simple
User=poe-search
WorkingDirectory=/opt/poe-search
ExecStart=/opt/poe-search/venv/bin/python gui_launcher.py
Restart=always

[Install]
WantedBy=multi-user.target
```
