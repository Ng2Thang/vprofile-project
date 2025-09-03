pipeline {
	agent any

    environment {
        // It's a good practice to use a virtual environment for Python projects
        VENV_DIR = ".venv"

        // Nexus Configuration for a PyPI repository
        // NOTE: You might need to adjust NEXUS_REPOSITORY_NAME if your PyPI repository in Nexus has a different name.
        NEXUS_REPOSITORY_NAME = "python-project"
        // NEXUS_URL             = "localhost:8081"
        NEXUS_URL           = "1fa176eccd8d.ngrok-free.app"
        NEXUS_PYPI_REPO_URL = "https://${NEXUS_URL}/repository/${NEXUS_REPOSITORY_NAME}/"
        NEXUS_CREDENTIAL_ID = "NEXUS_CREDENTIAL_ID"
    }
	
    stages {
        
        stage('Setup and Install Dependencies') {
            steps {
                echo "--- Cloning source and installing dependencies ---"
                // Clean the workspace to ensure no artifacts from previous builds interfere.
                cleanWs()
                // This step checks out the repository configured for this Jenkins job.
                // The 'src' directory should be at the root of your repository.
                checkout scm
                echo "Source code checked out successfully."

                script {
                    // Use python3, assuming it's available on the agent.
                    // You might need to configure a Python tool in Jenkins Global Tool Configuration.
                    def python_executable = "python3.11"

                    // Clean up previous virtual environment if it exists
                    if (fileExists(VENV_DIR)) {
                        sh "rm -rf ${VENV_DIR}"
                    }
                    // Create a new virtual environment
                    sh "${python_executable} -m venv ${VENV_DIR}"

                    // The activate script path is different on Windows vs. Unix-like systems.
                    // This example assumes a Unix-like agent.
                    sh """
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest pytest-cov flake8 pylint bandit build twine
                    """
                }
            }
        }

        stage('Linting') {
            steps {
                script {
                    try {
                        echo "--- Running linter ---"
                        sh """
                        set -e
                        . ${VENV_DIR}/bin/activate
                        flake8 src
                        """
                        echo "Linting passed."
                    } catch (any) {
                        echo "Linting failed, but continuing."
                        // Mark the build as unstable to provide a visual cue of the non-critical failure.
                        // currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }

        stage('Pylint Analysis') {
            steps {
                script {
                    try {
                        echo "--- Running Pylint analysis ---"
                        sh """
                        set -e
                        . ${VENV_DIR}/bin/activate
                        pylint src -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" --output=pylint-report.txt
                        """
                        echo "Pylint analysis passed."
                    } catch (any) {
                        echo "Pylint analysis found issues. See the pylint-report.txt for details."
                        // Mark the build as unstable to provide a visual cue of the non-critical failure.
                        // currentBuild.result = 'UNSTABLE'
                    } finally {
                        // Always archive the report, regardless of success or failure.
                        if (fileExists('pylint-report.txt')) {
                            echo "Archiving Pylint report..."
                            archiveArtifacts artifacts: 'pylint-report.txt'
                        }
                    }
                }
            }
        }

        stage('Security Analysis (Bandit)') {
            steps {
                script {
                    try {
                        echo "--- Running security analysis with Bandit ---"
                        sh """
                        set -e
                        . ${VENV_DIR}/bin/activate
                        bandit -r ./src --format json --output bandit-report.json
                        """
                        echo "Bandit analysis passed with no high-severity issues."
                    } catch (any) {
                        echo "Bandit found potential security issues. See the bandit-report.json for details."
                        // Mark the build as unstable. Bandit exits with a non-zero code if issues are found.
                        // currentBuild.result = 'UNSTABLE'
                    } finally {
                        // Always archive the report.
                        if (fileExists('bandit-report.json')) {
                            echo "Archiving Bandit report..."
                            archiveArtifacts artifacts: 'bandit-report.json'
                        }
                    }
                }
            }
        }

        stage('Unit Test') {
            steps {
                script {
                    try {
                        echo "--- Running unit tests ---"
                        // Run pytest with coverage. This step might fail if there are test failures,
                        // which is caught below. The --junitxml report is generated by pytest regardless.
                        sh ". ${VENV_DIR}/bin/activate && coverage run --source=src -m pytest --junitxml=xunit-reports.xml tests/"
                        echo "Unit tests passed."
                    } catch (any) {
                        echo "Unit tests failed. Marking build as unstable."
                        // Mark the build as unstable to allow the pipeline to continue while still indicating a problem.
                        currentBuild.result = 'UNSTABLE'
                    } finally {
                        echo "--- Generating and stashing reports ---"
                        // Always generate the coverage XML report from the .coverage data file.
                        sh ". ${VENV_DIR}/bin/activate && coverage xml --omit=\"tests/*\""

                        // Stash reports for the SonarQube analysis stage. This must run
                        // even if tests fail so SonarQube can report on the failures and coverage.
                        stash name: 'sonar-reports', includes: 'coverage.xml, xunit-reports.xml'

                        // Archive reports as build artifacts for inspection.
                        archiveArtifacts artifacts: 'coverage.xml, xunit-reports.xml'
                    }
                }
            }
        }

        stage('SonarQube Analysis') {
            environment {
                scannerHome = tool 'sonar-scanner'
            }
            steps {
                script {
                    // Retrieve the reports stashed from the Unit Test stage
                    unstash 'sonar-reports'
                    // The 'withSonarQubeEnv' block will inject the SonarQube server URL and credentials
                    // configured in Jenkins -> Configure System -> SonarQube servers.
                    // The name must match the name of the server configuration.
                    withSonarQubeEnv('sonar-server') {
                        // The sonar-scanner will automatically pick up the sonar-project.properties file.
                        // We can still override properties here if needed, like the project version.
                        sh "${scannerHome}/bin/sonar-scanner -Dsonar.projectVersion=${currentBuild.number}"
                    }
                }
            }
        }

        stage('Build') {
            steps {
                echo "--- Building the project ---"
                // Clean previous build artifacts. The build tool will create 'dist/' and 'build/' in the root.
                sh "rm -rf dist/ build/ src/*.egg-info"
                // Build the project from the workspace root. The build tool will find
                // pyproject.toml or setup.py in the current directory and create the
                // distributable packages in the 'dist' directory.
                sh ". ${VENV_DIR}/bin/activate && python -m build"
            }
            post {
                success {
                    echo 'Archiving build artifacts...'
                    // Artifacts are in the root 'dist' directory after the build.
                    archiveArtifacts artifacts: 'dist/*'
                }
            }
        }
        

        stage('Publish to Nexus') {
            steps {
                echo "--- Publishing to Nexus ---"
                // Use Jenkins credentials for Nexus username and password
                withCredentials([
                    usernamePassword(
                        credentialsId: NEXUS_CREDENTIAL_ID,
                        usernameVariable: 'NEXUS_USERNAME',
                        passwordVariable: 'NEXUS_PASSWORD'
                    )]) {
                    sh """
                    . ${VENV_DIR}/bin/activate
                    twine upload --repository-url ${NEXUS_PYPI_REPO_URL} --username ${NEXUS_USERNAME} --password ${NEXUS_PASSWORD} dist/*
                    """
                }
            }
        }
    }

    post {
        always {
            script {
                // Ensure the 'Google Chat Notification' plugin is installed in Jenkins.
                // Also, configure a 'Secret text' credential with the ID 'google-chat-webhook'
                // containing your Google Chat space's webhook URL.

                def jobName = env.JOB_NAME
                def buildNumber = env.BUILD_NUMBER
                def buildStatus = currentBuild.currentResult
                def buildUrl = env.BUILD_URL
                def message

                if (buildStatus == 'SUCCESS') {
                    message = "✅ *${jobName}* #${buildNumber} - *SUCCESS* (<${buildUrl}|Open>)"
                } else if (buildStatus == 'UNSTABLE') {
                    message = "⚠️ *${jobName}* #${buildNumber} - *UNSTABLE* (<${buildUrl}|Open>)"
                } else { // Handles FAILURE, ABORTED, etc.
                    message = "❌ *${jobName}* #${buildNumber} - *${buildStatus}* (<${buildUrl}|Open>)"
                }

                 withCredentials([string(credentialsId: 'google-chat-webhook', variable: 'GOOGLE_CHAT_WEBHOOK_URL')]) {
                    googlechatnotification(url: GOOGLE_CHAT_WEBHOOK_URL, message: message)
                }
            }

            echo 'Pipeline finished. Cleaning up workspace.'
            // Clean up the virtual environment
            sh "rm -rf ${VENV_DIR}"

        }
    }
}
