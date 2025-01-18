import logging

from flask import Blueprint, request, render_template, current_app as app


honey_p = Blueprint('honey_p', __name__)


@honey_p.route('/adminpanel', methods=['GET', 'POST'])
def honeywork():
    client_ip = request.remote_addr  #remote addr = ip
    error = None
    honeypot_logger = logging.getLogger('honeypot')

    if request.method == 'POST':
        honeypot_logger.warning(f'HP activity ip: {client_ip}: {request.form}')
        error = "Failed login attempt. Please check your username and password."
        return render_template('fadminpanel.html', error=error)

    honeypot_logger.warning(f'HP activity ip: {client_ip}: GET request to /adminpanel')
    return render_template('fadminpanel.html', error=error)
