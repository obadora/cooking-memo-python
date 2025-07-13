#!/bin/bash

# EC2 Amazon Linux 2 setup script for cooking-memo-python

# Update system
sudo yum update -y

# Install Docker
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo yum install -y git

# Clone repository (replace with your actual repository)
# git clone https://github.com/your-username/Recipe.git
# cd Recipe/cooking-memo-python

# Create environment file
cat > .env << EOF
DATABASE_URL=mysql+aiomysql://admin:password@your-rds-endpoint.amazonaws.com:3306/cooking_memo
MYSQL_ROOT_PASSWORD=password
MYSQL_DATABASE=cooking_memo
MYSQL_USER=admin
MYSQL_PASSWORD=password
CORS_ORIGINS=https://your-cloudfront-domain.cloudfront.net
EOF

# Build and run with Docker Compose
docker-compose up -d

# Configure nginx proxy (optional)
sudo yum install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Create nginx config for FastAPI
sudo tee /etc/nginx/conf.d/cooking-memo.conf > /dev/null << EOF
server {
    listen 80;
    server_name your-ec2-domain.amazonaws.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo systemctl restart nginx

echo "Setup complete! Your FastAPI application should be running on port 8000"
echo "Access via: http://your-ec2-public-ip"