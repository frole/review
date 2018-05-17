if [[ $1 = "-r" || $1 = "--reinit" ]]; then
	python articles_coclust.py &
fi
FLASK_APP=webinterface.py flask run
# Running on http://localhost:5000/