# 🚀 CAPTCHA API v2.0

A modern, async CAPTCHA generation and verification API built with Quart, MongoDB, and comprehensive system monitoring.

## Features

✨ **Core Features:**
- 🎨 Dynamic CAPTCHA image generation with customizable grid and numbers
- ✅ Async CAPTCHA verification with accuracy tracking
- 📊 Real-time statistics dashboard with charts
- 💾 MongoDB async database with Motor
- ⚙️ System monitoring (CPU, RAM, Disk usage)
- 📈 Historical data tracking and analytics
- 🏥 Health check endpoints
- 🐳 Docker & Docker Compose support

## Project Structure

```
owncaptcha/
├── config/
│   ├── __init__.py
│   └── settings.py           # Configuration and environment variables
├── models/
│   ├── __init__.py
│   ├── captcha_model.py      # CAPTCHA data model
│   └── system_stats_model.py # System statistics model
├── routes/
│   ├── __init__.py
│   ├── captcha_routes.py     # CAPTCHA endpoints
│   ├── api_routes.py         # Statistics endpoints
│   └── dashboard_routes.py   # Dashboard endpoints
├── services/
│   ├── __init__.py
│   ├── database_service.py   # MongoDB connection & management
│   ├── captcha_service.py    # CAPTCHA generation logic
│   └── system_service.py     # System monitoring logic
├── utils/
│   ├── __init__.py
│   └── helpers.py            # Helper functions
├── app.py                    # Main application file
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables example
├── Dockerfile               # Docker container config
├── docker-compose.yml       # Docker Compose config
└── README.md               # This file
```

## Installation

### Prerequisites
- Python 3.8+
- MongoDB 4.4+
- pip or conda

### Local Setup

1. **Clone the repository**
```bash
cd owncaptcha
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your MongoDB connection details
```

5. **Run the application**
```bash
python app.py
```

The API will be available at `http://localhost:8000`

### Docker Setup

1. **Start with Docker Compose**
```bash
docker-compose up -d
```

2. **Access the application**
- API: http://localhost:8000
- Dashboard: http://localhost:8000/dashboard
- MongoDB: localhost:27017

3. **Stop the application**
```bash
docker-compose down
```

## API Endpoints

### CAPTCHA Endpoints

**Generate CAPTCHA**
```
GET /api/captcha
```
Response:
```json
{
  "success": true,
  "captcha_id": "abc123def456...",
  "image": "/api/images/abc123def456....png",
  "numbers": [45, 12, 89, ...]
}
```

**Verify CAPTCHA**
```
POST /api/verify/<captcha_id>/<user_answer>
```
Response:
```json
{
  "success": true,
  "correct": true,
  "message": "Correct! ✓"
}
```

**Get Image**
```
GET /api/images/<captcha_id>
```

### Statistics Endpoints

**Get CAPTCHA Statistics**
```
GET /api/stats
```
Response:
```json
{
  "total_generated": 1250,
  "total_verified": 1100,
  "total_correct": 987,
  "accuracy_rate": 89.73,
  "generated_last_hour": 45,
  "generated_last_24h": 320,
  "verified_last_hour": 38,
  "verified_last_24h": 280
}
```

**Get System Statistics**
```
GET /api/system/stats
```
Response:
```json
{
  "cpu_percent": 12.5,
  "cpu_count": 4,
  "memory_percent": 45.2,
  "memory_used_mb": 2048,
  "memory_total_mb": 4096,
  "disk_percent": 65.3,
  "disk_used_gb": 250.5,
  "disk_total_gb": 500.0
}
```

**Get System History**
```
GET /api/system/history
```

**Get System Summary**
```
GET /api/system/summary
```

### Dashboard

**Access Dashboard**
```
GET /dashboard
```
Open in browser for real-time monitoring with charts and statistics.

### Health Check

**Health Status**
```
GET /api/health
```

## Configuration

Edit `.env` file to customize:

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=captcha_db

# Application
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=False

# CAPTCHA
CAPTCHA_SIZE=1000
CAPTCHA_GRID_SIZE=700
CAPTCHA_OUTPUT_DIR=captchas
CAPTCHA_IMAGE_PATH=octopus.png

# Monitoring
SYSTEM_STATS_INTERVAL=10
HISTORY_RETENTION_DAYS=7
```

## Database Schema

### Captcha Stats Collection

```javascript
{
  _id: ObjectId,
  captcha_id: String,           // Unique identifier
  generated_at: ISODate,        // Generation timestamp
  verified_at: ISODate,         // Verification timestamp
  answer: Number,               // Correct answer
  user_answer: Number,          // User's answer
  is_correct: Boolean,          // Verification result
  numbers: [Number],            // Grid numbers
  attempts: Number              // Attempt count
}
```

### System Stats Collection

```javascript
{
  _id: ObjectId,
  timestamp: ISODate,           // Record time
  cpu_percent: Number,          // CPU usage %
  memory_percent: Number,       // Memory usage %
  disk_percent: Number,         // Disk usage %
  memory_used_mb: Number,       // Used memory
  memory_available_mb: Number,  // Available memory
  memory_total_mb: Number,      // Total memory
  disk_used_gb: Number,         // Used disk
  disk_total_gb: Number,        // Total disk
  disk_free_gb: Number          // Free disk
}
```

## Async Operations

All database operations are fully async using Motor:

```python
# Generate CAPTCHA (async)
captcha_id, answer, numbers = await captcha_service.generate_captcha()

# Verify CAPTCHA (async)
is_correct = await captcha_service.verify_captcha(captcha_id, user_answer)

# Get statistics (async)
stats = await captcha_service.get_statistics()

# Record system stats (async)
await system_service.record_stats()
```

## Dashboard Features

📊 **Real-time Metrics:**
- Total CAPTCHAs generated
- Total verified
- Correct answers
- Accuracy rate
- Generated in last hour/24 hours

📈 **Charts:**
- CPU usage over 24 hours
- Memory usage over 24 hours

⚙️ **System Resources:**
- CPU status and usage
- Memory status and availability
- Disk storage status

🔄 **Auto-refresh:** Data updates every 10 seconds

## Performance

- ⚡ Async/await for concurrent operations
- 🗄️ MongoDB indexing for fast queries
- 📦 TTL indexes for automatic cleanup
- 🎯 Efficient database queries
- 💨 Optimized image generation

## Error Handling

All endpoints include comprehensive error handling:

```json
{
  "success": false,
  "error": "Error description",
  "message": "Detailed message"
}
```

## Logging

Logs are written to console with timestamps:

```
2024-01-15 10:30:45 - captcha_service - INFO - Generated CAPTCHA: abc123...
2024-01-15 10:30:47 - system_service - INFO - Recorded system stats
```

## Development

### Run Tests
```bash
pytest tests/
```

### Code Style
```bash
# Format code
black .

# Lint
flake8 .
```

## Deployment

### Production Checklist

- [ ] Set `APP_DEBUG=False`
- [ ] Use strong MongoDB credentials
- [ ] Set proper CORS policies
- [ ] Enable HTTPS
- [ ] Configure firewall
- [ ] Set up logging aggregation
- [ ] Configure backup strategy
- [ ] Use environment variables for secrets

### Scaling

- Use MongoDB replica sets for high availability
- Deploy multiple app instances behind a load balancer
- Use CDN for static assets
- Implement rate limiting
- Cache frequently accessed data

## Troubleshooting

### MongoDB Connection Error
```bash
# Check MongoDB is running
mongosh localhost:27017

# Verify connection string in .env
MONGODB_URL=mongodb://localhost:27017
```

### Port Already in Use
```bash
# Use different port
APP_PORT=8001
```

### Image Generation Issues
- Ensure `octopus.png` exists in root directory
- Check font files: `/usr/share/fonts/truetype/liberation/`

## Support & Contributing

For issues, questions, or contributions, please open an issue or submit a pull request.

## License

MIT License - See LICENSE file for details

## Changelog

### v2.0
- ✨ Complete rewrite with modular structure
- 🔄 Async operations with Motor
- 📊 Enhanced dashboard with charts
- ⚙️ Advanced system monitoring
- 🗂️ Organized file structure
- 📦 Docker support
- 🧪 Comprehensive error handling

### v1.0
- Initial release
