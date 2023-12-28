# LOG8415E_Project: Scaling Databases and Implementing Cloud Design Patterns

This repository contains everything I, Eric Huard, used to complete the final project of the course LOG8415E: Advanced concepts of Cloud Computing at Polytechnique Montréal.


Link for the presentation : https://youtu.be/b4A5zQb1Bhk

## How to run the code:
First of all, you will need to get your own access keys to Amazon Web Services. You specifically need :
- aws_access_key_id;
- aws_secret_access_key;
- aws_session_token.

These need to be properly configured on your computer at /.aws/credentials.
Once all keys are set up, run pip install -r requirements, eventually in a virtual environment if you prefer . It will verify and install all needed libraries.

Once the steps above are done, you can run python3 ./setup/main.py in order to setup all the instances. This will take some time (more than 5 minutes), so you can go grab a cup of coffee in the meantime. Be careful, it requires you to be in the project directory to run properly. It also needs you to have the write permission. You will also need to make sure the key created has the right permissions to connect to the instances using SSH. If it fails because you have too large permissions, please change them and run the program again : it will not delete the existing key and you will be able to connect with no issue.

To get the benchmark results, run python3 ./tests/perform_benchmarks.py. It will form the benchmarks on the distant machines and fetch them in your local directory (in /tests/mark_results) after one minute. 

In order to access the application, look at the addresses printed at the end of the initialization. They sould look like that  http://ec2-3-235-249-218.compute-1.amazonaws.com/read and   http://ec2-3-235-249-218.compute-1.amazonaws.com/write. On these pages, you can either submit a read or a write request, depending on which page your are currently on.

It is possible that some parts of the initialization went wrong. Namely, you may have to connect through SSH to the gatekeeper, trusted_host and proxy instances and run these commands:
- on the gatekeeper: 
  - sudo pip3 install flask requests
  - sudo python3 flask_app.py
- on the trusted host:
  - pip3 install flask requests sqlfluff
  - python3 flask_app.py
- on the proxy: 
  - pip3 install flask ping3 mysql-connector-python 
  - python3 flask_app.py
  
The public dns of these instances can be found in data.json. They are also printed during initialization.

