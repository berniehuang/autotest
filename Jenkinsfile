pipeline {
  agent any
  stages {
    stage('install') {
      steps {
        sh 'python setup.py install'
      }
    }

    stage('build') {
      steps {
        echo 'Hello World'
      }
    }

  }
}