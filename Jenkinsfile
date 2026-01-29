pipeline {
  agent {
    label 'docker-agent'
  }

  environment {
    DOCKERHUB_USER = "khanazal"
    IMAGE_TAG      = "V${BUILD_NUMBER}"

    AWS_REGION  = "eu-north-1"
    EKS_CLUSTER = "notes-app-cluster"
  }

  stages {

    stage('Checkout Code') {
      steps {
        git branch: 'main', url: 'https://github.com/AZAL-KHAN/notes-app-microservices.git'
      }
    }

    stage('DockerHub Login') {
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'dockerhub-creds',
          usernameVariable: 'DOCKER_USER',
          passwordVariable: 'DOCKER_PASS'
        )]) {
          sh '''
            echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
          '''
        }
      }
    }

    stage('Build & Push Auth Service Image') {
      steps {
        sh '''
          docker build -t $DOCKERHUB_USER/notesapp-auth:$IMAGE_TAG auth-service
          docker push $DOCKERHUB_USER/notesapp-auth:$IMAGE_TAG
        '''
      }
    }

    stage('Build & Push Backend Service Image') {
      steps {
        sh '''
          docker build -t $DOCKERHUB_USER/notesapp-backend:$IMAGE_TAG backend-service
          docker push $DOCKERHUB_USER/notesapp-backend:$IMAGE_TAG
        '''
      }
    }

    stage('Build & Push Frontend Service Image') {
      steps {
        sh '''
          docker build -t $DOCKERHUB_USER/notesapp-frontend:$IMAGE_TAG frontend-service
          docker push $DOCKERHUB_USER/notesapp-frontend:$IMAGE_TAG
        '''
      }
    }

    stage('Inject Image Tags into K8s Manifests') {
      steps {
        sh '''
          sed -i "/image:/s/BUILD_TAG/$IMAGE_TAG/g" k8s/*/deployment*.yml
        '''
      }
    }

    stage('Deploy to AWS EKS') {
      steps {
        withAWS(credentials: 'aws-creds', region: "${AWS_REGION}") {
          sh '''
            aws eks update-kubeconfig \
              --region $AWS_REGION \
              --name $EKS_CLUSTER

            kubectl apply -f k8s/namespace.yml
            kubectl apply -R -f k8s/

          '''
        }
      }
    }
  }

  post {

    failure {
      emailext(
        subject: "❌ Jenkins Build Failed: ${JOB_NAME} #${BUILD_NUMBER}",
        body: """
Hello,

The Jenkins build has FAILED.

Job Name  : ${JOB_NAME}
Build No  : ${BUILD_NUMBER}

Check the build logs here:
${BUILD_URL}

Regards,
Jenkins
""",
        to: "your-email@example.com"
      )
    }

    always {
      sh 'docker logout || true'
      cleanWs()
    }

    success {
      echo "✅ Successfully deployed build ${IMAGE_TAG} to EKS"
    }
  }
}
