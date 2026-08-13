"""Pipeline Generator produces GitLab CI and Jenkinsfile pipelines.
"""

class PipelineGenerator:
    """Generates non-GHA pipeline scripts."""

    def generate_gitlab_ci(self, project_name: str, language: str) -> str:
        """Returns .gitlab-ci.yml contents."""
        image = "python:3.12"
        if language == "Node.js":
            image = "node:20"

        return f"""stages:
  - checkout
  - install
  - lint
  - test
  - build
  - security
  - docker_build
  - deploy

variables:
  DOCKER_IMAGE: {project_name.lower()}:$CI_COMMIT_SHA

image: {image}

before_script:
  - echo "Starting pipeline stage..."

checkout:
  stage: checkout
  script:
    - echo "Checking out repository..."

install_dependencies:
  stage: install
  script:
    - if [ "{language}" = "Python" ]; then pip install -r requirements.txt; fi
    - if [ "{language}" = "Node.js" ]; then npm ci; fi

lint:
  stage: lint
  script:
    - echo "Running lint check..."

test:
  stage: test
  script:
    - echo "Running unit tests..."

build:
  stage: build
  script:
    - echo "Running compile/build step..."

security_scan:
  stage: security
  script:
    - echo "Running security scan checks..."
  allow_failure: true

docker_build:
  stage: docker_build
  image: docker:stable
  services:
    - docker:dind
  script:
    - docker build -t $DOCKER_IMAGE .

deploy:
  stage: deploy
  script:
    - echo "Deploying image $DOCKER_IMAGE to target environment..."
"""

    def generate_jenkinsfile(self, project_name: str) -> str:
        """Returns Jenkinsfile contents."""
        return f"""pipeline {{
    agent any

    environment {{
        DOCKER_IMAGE = "{project_name.lower()}:${{env.BUILD_NUMBER}}"
    }}

    stages {{
        stage('Code Checkout') {{
            steps {{
                checkout scm
            }}
        }}

        stage('Dependency Install') {{
            steps {{
                echo 'Installing dependencies...'
            }}
        }}

        stage('Lint') {{
            steps {{
                echo 'Running lint validation...'
            }}
        }}

        stage('Testing') {{
            steps {{
                echo 'Running unit test suites...'
            }}
        }}

        stage('Build') {{
            steps {{
                echo 'Compiling/building code...'
            }}
        }}

        stage('Security Scan') {{
            steps {{
                echo 'Performing static code analysis security scans...'
            }}
        }}

        stage('Docker Build') {{
            steps {{
                sh "docker build -t ${{DOCKER_IMAGE}} ."
            }}
        }}

        stage('Deploy') {{
            steps {{
                echo "Deploying ${{DOCKER_IMAGE}} to target..."
            }}
        }}
    }}
}}
"""
