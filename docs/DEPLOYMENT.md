# Deployment Guide

## Docker Deployment
```bash
docker-compose up -d
```

## Cloud Deployment (AWS/Azure/GCP)

### Using Docker
1. Build image: `docker build -t cara-bot .`
2. Push to registry
3. Deploy to cloud service

### Environment Variables
- `ANTHROPIC_API_KEY` - Required
- `PORT` - Default 8501

## Production Considerations

- Add authentication
- Set up HTTPS
- Configure rate limiting
- Add monitoring/logging
- Set up backups