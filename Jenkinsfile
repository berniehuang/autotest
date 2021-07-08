pipeline {
  agent any
  stages {
    stage('Install') {
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
      parallel {
        stage('Mail') {
          steps {
            mail(subject: 'Test', body: 'hello')
            sh 'ls -l'
            echo 'send mail'
          }
        }

        stage('upload') {
          steps {
            echo 'upload data'
          }
        }

      }
    }

  }
}