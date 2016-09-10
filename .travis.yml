language: python

# Cache the pip files
cache:
  directories:
    - $HOME/.cache/pip
    - $HOME/.nvm
    - node_modules
    - wger/node_modules

# Use container infrastructure
# http://blog.travis-ci.com/2014-12-17-faster-builds-with-container-based-infrastructure/
sudo: false

# Python versions to test
python:
  - "2.7"
  - "3.4"
  - "3.5"

# Manually define here the combinations environment variables to test
# https://github.com/travis-ci/travis-ci/issues/1519
env:
  - TEST_MOBILE=True  DB=postgresql TRAVIS_NODE_VERSION="4"
  - TEST_MOBILE=True  DB=sqlite     TRAVIS_NODE_VERSION="4"
  - TEST_MOBILE=False DB=postgresql TRAVIS_NODE_VERSION="4"
  - TEST_MOBILE=False DB=sqlite     TRAVIS_NODE_VERSION="4"

# Install the application
install:
  # Update nvm and set wanted Node version.
  # We update nvm using the script method instead of git, which is selected
  # automatically, as git won't work because the $HOME/.nvm is not a git
  # repository and the directory is not empty.
  - curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.31.4/install.sh | METHOD=script bash
  - . $HOME/.nvm/nvm.sh
  - nvm install $TRAVIS_NODE_VERSION
  - nvm use $TRAVIS_NODE_VERSION

  # Install requirements
  - pip install -r requirements_devel.txt
  - npm install
  - if [[ "$DB" = "postgresql" ]]; then pip install psycopg2; fi

  # Setup application
  - if [[ "$DB" = "sqlite" ]]; then invoke create_settings; fi
  - if [[ "$DB" = "postgresql" ]]; then invoke create_settings --database-type postgresql; fi

# Create test databases
before_script:
  - if [[ "$DB" = "postgresq" ]]; then psql -c 'DROP DATABASE IF EXISTS test_wger;' -U postgres; fi
  - if [[ "$DB" = "postgresql" ]]; then psql -c 'CREATE DATABASE test_wger;' -U postgres; fi

# Do the tests
script:
  # Formatting
  - pep8 wger

  # Javascript linting
  - gulp lint

  # Regular application
  - coverage run --source='.' ./manage.py test


  # Code coverage
  - coverage report
