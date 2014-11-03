kill `ps -f | grep gunicorn_operator_man.py | grep -v grep | awk '{print $2}'`

PROJECT_HOME="/root/workspace/OperatorCenter/Operator/applications/"

cd $PROJECT_HOME

gunicorn -c gunicorn_operator_man.py operator_app:app
