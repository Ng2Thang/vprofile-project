pipeline {
	agent any

    environment {
        // It's a good practice to use a virtual environment for Python projects
        VENV_DIR = ".venv"

        // Nexus Configuration for a PyPI repository
        // NOTE: You might need to adjust NEXUS_REPOSITORY_NAME if your PyPI repository in Nexus has a different name.
        NEXUS_REPOSITORY_NAME = "vprofile-pypi-release"
        NEXUS_URL             = "172.31.40.209:8081"
        NEXUS_PYPI_REPO_URL   = "http://${NEXUS_URL}/repository/${NEXUS_REPOSITORY_NAME}/"
        NEXUS_CREDENTIAL_ID   = "nexuslogin"
    }
	
    stages {
        
        stage('Setup and Install Dependencies') {
            steps {
                echo "--- Cloning source and installing dependencies ---"
                // This step checks out the repository configured for this Jenkins job.
                // The 'src' directory should be at the root of your repository.
                checkout scm

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
                    pip install -r src/requirements.txt
                    pip install pytest pytest-cov flake8 build twine
                    """
                }
            }
        }

        stage('Linting') {
            steps {
                echo "--- Running linter ---"
                // Run a linter like flake8 to check code quality
                // sh ". ${VENV_DIR}/bin/activate && flake8 ."
            }
        }

        stage('Unit Test') {
            steps {
                echo "--- Running unit tests ---"
                // Run tests with pytest and generate a coverage report
                // sh ". ${VENV_DIR}/bin/activate && pytest --cov=. --cov-report=xml"
            }
            post {
                success {
                    echo 'Unit tests passed.'
                    // You can archive coverage reports here if needed.
                    // For example, if you have the Cobertura plugin installed:
                    // cobertura coberturaReportFile: 'coverage.xml'
                }
            }
        }

        stage('Build') {
            steps {
                echo "--- Building the project ---"
                // Clean psrevious build artifacts
                // sh "rm -rf dist/ build/ *.egg-info"
                // Build the wheel and source distribution using the 'build' package
                // sh ". ${VENV_DIR}/bin/activate && python -m build"
            }
            post {
                success {
                    echo 'Archiving build artifacts...'
                    // archiveArtifacts artifacts: 'dist/*'
                }
            }
        }

        // stage('Publish to Nexus') {
        //     steps {
        //         echo "--- Publishing to Nexus ---"
        //         // Use Jenkins credentials for Nexus username and password
        //         withCredentials([usernamePassword(credentialsId: NEXUS_CREDENTIAL_ID, usernameVariable: 'NEXUS_USERNAME', passwordVariable: 'NEXUS_PASSWORD')]) {
        //             sh """
        //             . ${VENV_DIR}/bin/activate
        //             twine upload --repository-url ${NEXUS_PYPI_REPO_URL} --username ${NEXUS_USERNAME} --password ${NEXUS_PASSWORD} dist/*
        //             """
        //         }
        //     }
        // }
    }

    post {
        always {
            echo 'Pipeline finished. Cleaning up workspace.'
            // Clean up the virtual environment
            sh "rm -rf ${VENV_DIR}"
        }
    }
}
