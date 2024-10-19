docker build -t flask-firebase-app .
docker tag flask-firebase-app gcr.io/my-flask-firebase-app/flask-firebase-app
docker push gcr.io/my-flask-firebase-app/flask-firebase-app
gcloud run deploy flask-firebase-app --image gcr.io/my-flask-firebase-app/flask-firebase-app  --platform managed  --region asia-southeast1 --allow-unauthenticated