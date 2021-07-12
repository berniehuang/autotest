pipeline {
  agent any
  triggers {
    gerrit(
      serverName: 'gerrit.office.iauto.com',
      gerritProjects: [[
        compareType: 'PLAIN',
        pattern: 'All-Users',
        branches: [[ compareType: 'PLAIN', pattern: 'master' ]]
      ]],
      triggerOnEvents: [
        changeMerged(),
        patchsetCreated(excludeDrafts: false, excludeNoCodeChange: false, excludeTrivialRebase: false)
      ]
    )
  }
  
  stages {
    stage('Install') {
      when {
        expression {
          BUILD_EXPRESSION
        }

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
            sh 'ls -l'
          }
        }

        stage('deploy') {
          steps {
            echo 'deploy'
            sh 'pwd'
          }
        }

        stage('compile') {
          steps {
            echo 'compile'
            sh 'echo $PATH'
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
  environment {
    BUILD_EXPRESSION = false
  }
}
