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
                    pip install pytest pytest-cov flake8 build twine
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
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }

        stage('Unit Test') {
            steps {
                echo "--- Running unit tests ---"
                // Run tests from the workspace root to simplify path management.
                // --cov=src: Measure coverage for the 'src' directory.
                // --cov-report=xml:coverage.xml: Generate the report at the workspace root.
                // By not using --source, coverage paths are generated relative to the project root (e.g., 'src/app.py'),
                // which is often more compatible with external tools like SonarQube.
                // tests/: Tell pytest to discover tests in the 'tests' directory.
                sh ". ${VENV_DIR}/bin/activate && coverage run --source=src -m pytest tests/ && coverage xml -o coverage.xml"
            }
            post {
                success {
                    echo 'Unit tests passed.'
                    echo 'Stashing coverage report for SonarQube stage...'
                    stash name: 'coverage-report', includes: 'coverage.xml'
                    echo 'Archiving test reports...'
                    archiveArtifacts artifacts: 'coverage.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            environment {
                scannerHome = tool 'sonar-scanner'
            }
            steps {
                script {
                    // Retrieve the coverage file stashed from the Unit Test stage
                    unstash 'coverage-report'
                    // The 'withSonarQubeEnv' block will inject the SonarQube server URL and credentials
                    // configured in Jenkins -> Configure System -> SonarQube servers.
                    // The name must match the name of the server configuration.
                    withSonarQubeEnv('sonar-server') {
                        sh """
                        ${scannerHome}/bin/sonar-scanner \\
                            -Dsonar.projectKey=python-project \\
                            -Dsonar.projectName=python-project \\
                            -Dsonar.projectVersion=${currentBuild.number} \\
                            # Since the coverage report now contains full paths (e.g., 'src/app.py'),
                            # we tell SonarQube to look for sources from the project root.
                            -Dsonar.sources=src \\
                            -Dsonar.tests=tests \\
                            -Dsonar.python.coverage.reportPath=coverage.xml \\
                            -Dsonar.scm.disabled=true
                        """
                    }
                }
            }
        }

        // stage('Build') {
        //     steps {
        //         echo "--- Building the project ---"
        //         // The build process should run inside the 'src' directory where setup.py/pyproject.toml is located.
        //         dir('src') {
        //             // Clean previous build artifacts
        //             sh "rm -rf dist/ build/ *.egg-info"
        //             // Build the wheel and source distribution using the 'build' package
        //             // Note the path to the activate script is relative to the 'src' directory.
        //             sh ". ../${VENV_DIR}/bin/activate && python -m build"
        //         }
        //     }
        //     post {
        //         success {
        //             echo 'Archiving build artifacts...'
        //             // Artifacts are in the 'src/dist' directory after the build.
        //             archiveArtifacts artifacts: 'src/dist/*'
        //         }
        //     }
        // }
        

        // stage('Publish to Nexus') {
        //     steps {
        //         echo "--- Publishing to Nexus ---"
        //         // Use Jenkins credentials for Nexus username and password
        //         withCredentials([usernamePassword(credentialsId: NEXUS_CREDENTIAL_ID, usernameVariable: 'NEXUS_USERNAME', passwordVariable: 'NEXUS_PASSWORD')]) {
        //             sh """
        //             . ${VENV_DIR}/bin/activate
        //             twine upload --repository-url ${NEXUS_PYPI_REPO_URL} --username ${NEXUS_USERNAME} --password ${NEXUS_PASSWORD} src/dist/*
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
