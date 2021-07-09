pipeline {
  agent any
  environment {
    BUILD_EXPRESSION = true
  }
  stages {
    stage('Install') {
      when {
         expression { BUILD_EXPRESSION }
      }
      steps {
        echo 'Good'
      }
    }

    stage('Build') {
      parallel {
        stage('build') {
          steps {
            echo 'Hello World'
          }
        }

        stage('deploy') {
          steps {
            echo 'deploy'
          }
        }

      }
    }

    stage('Run') {
      parallel {
        stage('Run') {
          steps {
            echo 'running'
            timestamps()
          }
        }

        stage('Startup') {
          steps {
            echo 'startup'
          }
        }

      }
    }

    stage('Test') {
      steps {
        echo 'test'
      }
    }

    stage('Mail') {
      steps {
        mail(subject: 'Test', body: 'hello')
        sh 'ls -l'
        echo 'send mail'
      }
    }

  }
}
