pipeline {
  agent any
  stages {
    stage('install') {
      steps {
        echo 'Good'
      }
    }

    stage('build') {
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

    stage('run') {
      steps {
        echo 'running'
      }
    }

    stage('test') {
      steps {
        echo 'test'
      }
    }

  }
}