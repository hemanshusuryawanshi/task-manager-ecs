# Task Manager — AWS ECS Fargate Demo

A task management app deployed on AWS using a fully containerized, serverless-infrastructure pipeline. Built as a capstone project for the AWS with Python certification course at Symbiosis.

**Live demo:** open `task-manager-frontend.html` in a browser — it's pre-configured to talk to the deployed API.

## Screenshots

**Dashboard — tasks loaded**


**Empty state**


**Mobile view**


## Architecture

<img width="893" height="444" alt="image" src="https://github.com/user-attachments/assets/f7fcde8b-8a09-43a8-a9f6-f5edd42152dc" />

Flask app  →  Docker image  →  Amazon ECR  →  ECS Fargate task  →  Application Load Balancer  →  DynamoDB

- **Flask** — REST API serving task CRUD operations
- **Docker** — packages the Flask app into a container image
- **Amazon ECR** — stores the container image
- **ECS Fargate** — runs the container serverlessly, no EC2 instances to manage
- **Application Load Balancer (ALB)** — routes public HTTP traffic to the running task, health-checks `/health`
- **DynamoDB** — stores tasks (`tasks-hemanshu2026` table, partition key `task_id`)
- **flask-cors** — enables the frontend (served as a local static file) to call the API cross-origin

The frontend is a single static HTML/CSS/JS file with no build step — it calls the ALB URL directly from the browser.

## API endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check, used by the ALB target group |
| GET | `/tasks` | List all tasks |
| POST | `/tasks` | Create a task — body: `{ "title": str, "description": str (optional), "status": str (optional, default "pending") }` |
| GET | `/tasks/<task_id>` | Get a single task |
| PUT | `/tasks/<task_id>` | Update a task — body: any of `title`, `description`, `status` |
| DELETE | `/tasks/<task_id>` | Delete a task |

## Running locally

```bash
pip install -r requirements.txt
python app.py
```

The app expects AWS credentials configured (`aws configure`) with access to a DynamoDB table named `tasks-hemanshu2026` in `ap-south-1`, and runs on `http://localhost:5000`.

## Deploying

```bash
# Build
docker build -t task-manager-app-hemanshu2026 .

# Authenticate to ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-south-1.amazonaws.com

# Tag and push
docker tag task-manager-app-hemanshu2026:latest <account-id>.dkr.ecr.ap-south-1.amazonaws.com/task-manager-app-hemanshu2026:latest
docker push <account-id>.dkr.ecr.ap-south-1.amazonaws.com/task-manager-app-hemanshu2026:latest

# Roll out the new image on ECS
aws ecs update-service \
  --cluster task-manager-cluster-hemanshu2026 \
  --service <your-service-name> \
  --force-new-deployment \
  --region ap-south-1
```

## Project structure
.
├── app.py                        # Flask API
├── Dockerfile                    # Container build
├── requirements.txt              # Python dependencies
├── task-manager-frontend.html    # Static dashboard frontend
├── images/                       # Architecture diagram + screenshots
│   └── architecture-diagram.svg
└── .dockerignore
