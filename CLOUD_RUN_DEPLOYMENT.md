# Google Cloud Run Deployment Guide for Seed-VC

This guide will help you deploy the Seed-VC voice conversion application to Google Cloud Run.

## Prerequisites

- Google Cloud Platform (GCP) account with billing enabled
- Google Cloud SDK installed (`gcloud` CLI)
- Docker installed on your local machine (optional, for local testing)
- Appropriate GCP permissions for Cloud Run and Container Registry

## Fixed Issues

The following issues have been corrected for successful Cloud Run deployment:

### 1. **app_vc.py** - Main Application File
- **Fixed**: Replaced dummy "Hello World" Flask app with proper Gradio voice conversion application
- **Added**: Model loading functionality from HuggingFace
- **Added**: Support for custom model checkpoints
- **Fixed**: Proper PORT environment variable binding for Cloud Run
- **Added**: Error handling and user feedback

### 2. **Dockerfile** - Container Configuration
- **Fixed**: Removed invalid `--share False` arguments from CMD
- **Added**: `libsndfile1` system dependency for audio processing
- **Added**: `PYTHONUNBUFFERED=1` for proper logging in Cloud Run
- **Added**: `GRADIO_SERVER_NAME=0.0.0.0` for external access
- **Fixed**: Proper dynamic PORT binding using environment variable
- **Added**: Created cache directory for HuggingFace model downloads
- **Optimized**: Multi-stage build considerations

### 3. **requirements.txt** - Python Dependencies
- **Added**: Version pins for reproducibility and security
- **Added**: Missing critical dependencies:
  - `huggingface-hub>=0.16.0` - For model downloads
  - `pyyaml>=6.0` - For configuration files
  - `munch>=4.0.0` - For recursive configuration objects
  - `scipy>=1.10.0` - For scientific computing
- **Organized**: Dependencies by category for maintainability

### 4. **.dockerignore** - Build Optimization
- **Added**: Comprehensive ignore patterns to reduce image size
- **Excluded**: Model checkpoints (downloaded at runtime)
- **Excluded**: Virtual environments, IDE files, documentation
- **Result**: Significantly faster builds and smaller images

## Deployment Steps

### Step 1: Set Up GCP Project

```bash
# Set your project ID
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"  # Choose your preferred region

# Configure gcloud
gcloud config set project $PROJECT_ID
```

### Step 2: Enable Required APIs

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Container Registry API
gcloud services enable containerregistry.googleapis.com

# Enable Artifact Registry API (recommended for new projects)
gcloud services enable artifactregistry.googleapis.com
```

### Step 3: Build and Push Docker Image

#### Option A: Using Cloud Build (Recommended)

```bash
# Build and push image using Cloud Build
gcloud builds submit --tag gcr.io/$PROJECT_ID/seed-vc:latest

# Or with Artifact Registry
gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/seed-vc/app:latest
```

#### Option B: Using Local Docker

```bash
# Build locally
docker build -t gcr.io/$PROJECT_ID/seed-vc:latest .

# Push to GCR
docker push gcr.io/$PROJECT_ID/seed-vc:latest
```

### Step 4: Deploy to Cloud Run

```bash
# Deploy with recommended settings
gcloud run deploy seed-vc \
  --image gcr.io/$PROJECT_ID/seed-vc:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "HF_HUB_CACHE=/app/checkpoints/hf_cache"
```

### Important Cloud Run Configuration Notes

#### Memory and CPU Requirements
- **Minimum recommended**: 4GB RAM, 2 CPUs
- **For better performance**: 8GB RAM, 4 CPUs
- Voice conversion models require significant memory

#### Timeout Configuration
- Default timeout (300s) may be insufficient for large audio files
- Consider increasing to 900s (15 minutes) for production:
  ```bash
  --timeout 900
  ```

#### Cold Start Optimization
- First request after idle period will be slower due to model loading
- Consider setting minimum instances for production:
  ```bash
  --min-instances 1
  ```

#### Authentication
- The example above uses `--allow-unauthenticated` for public access
- For private use, remove this flag and configure IAM permissions

### Step 5: Access Your Application

After deployment, Cloud Run will provide a URL like:
```
https://seed-vc-xxxxx-uc.a.run.app
```

You can access the Gradio web interface at this URL.

## Environment Variables

You can set additional environment variables during deployment:

```bash
gcloud run deploy seed-vc \
  --image gcr.io/$PROJECT_ID/seed-vc:latest \
  --set-env-vars "HF_HUB_CACHE=/app/checkpoints/hf_cache,GRADIO_ANALYTICS_ENABLED=False"
```

## Local Testing Before Deployment

Test the Docker image locally before deploying:

```bash
# Build the image
docker build -t seed-vc-local .

# Run locally
docker run -p 8080:8080 \
  -e PORT=8080 \
  seed-vc-local

# Access at http://localhost:8080
```

## Troubleshooting

### Issue: Container fails to start
**Solution**: Check logs:
```bash
gcloud run services logs read seed-vc --region $REGION
```

### Issue: Out of memory errors
**Solution**: Increase memory allocation:
```bash
gcloud run services update seed-vc --memory 8Gi --region $REGION
```

### Issue: Timeout errors
**Solution**: Increase timeout:
```bash
gcloud run services update seed-vc --timeout 900 --region $REGION
```

### Issue: Model download fails
**Solution**: Ensure HuggingFace Hub is accessible and increase memory/timeout

### Issue: Cold start takes too long
**Solution**: Set minimum instances:
```bash
gcloud run services update seed-vc --min-instances 1 --region $REGION
```

## Cost Optimization

1. **Use autoscaling**: Don't set `--min-instances` unless necessary
2. **Right-size resources**: Start with 4GB RAM and adjust based on usage
3. **Monitor usage**: Use Cloud Monitoring to track requests and adjust
4. **Consider region**: Some regions are cheaper than others

## Monitoring and Logs

View logs in real-time:
```bash
gcloud run services logs tail seed-vc --region $REGION
```

View metrics in Cloud Console:
- Navigate to Cloud Run → seed-vc → Metrics
- Monitor: Request count, latency, memory usage, CPU usage

## Updating the Application

To deploy updates:

```bash
# Rebuild and deploy
gcloud builds submit --tag gcr.io/$PROJECT_ID/seed-vc:latest
gcloud run deploy seed-vc --image gcr.io/$PROJECT_ID/seed-vc:latest --region $REGION
```

## Security Recommendations

1. **Use Artifact Registry** instead of Container Registry for new projects
2. **Enable authentication** for production deployments
3. **Use Secret Manager** for sensitive configuration
4. **Implement rate limiting** to prevent abuse
5. **Regular security updates**: Keep dependencies updated

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Gradio Documentation](https://www.gradio.app/docs)
- [Seed-VC GitHub Repository](https://github.com/Plachtaa/seed-vc)
- [HuggingFace Model Hub](https://huggingface.co/Plachta/Seed-VC)

## Known Limitations

1. **GPU Support**: Cloud Run does not support GPUs. For GPU acceleration, consider:
   - Google Kubernetes Engine (GKE) with GPU nodes
   - Vertex AI for managed ML deployments
   - Compute Engine with GPU instances

2. **Model Loading Time**: First request after cold start will be slow (30-60s)

3. **File Upload Limits**: Gradio/Cloud Run may have file size limits for audio uploads

4. **Processing Time**: Large audio files may approach timeout limits

## Support

For issues specific to:
- **Seed-VC**: Visit [GitHub Issues](https://github.com/Plachtaa/seed-vc/issues)
- **Cloud Run**: Visit [Google Cloud Support](https://cloud.google.com/support)
- **This Deployment**: Check the commit history for recent fixes

---

**Last Updated**: 2025-10-12  
**Fixed By**: Repository maintenance update  
**Status**: ✅ Ready for deployment
