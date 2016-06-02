import os,json
from flask import Flask, request,redirect, url_for,send_from_directory, Response
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

UPLOAD_FOLDER = os.path.dirname(os.path.realpath(__name__))+ '/uploads/'
ALLOWED_EXTENSIONS= set(['json'])

app= Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    #TODO : change to rotating file handler thing
    file_handler = RotatingFileHandler('server.log',mode='a',maxBytes=1024000 )
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    with open('test_schema.json') as schema:
        schemaJson = json.load(schema)
        try:
            app.logger.debug("Before checking request json")
            
            #REMEMBER THIS FOREVER!
            with open(UPLOAD_FOLDER+filename) as file:
                validate(json.load(file), schemaJson)
            app.logger.debug("after checking request.json")
            resp_str = {
                "status" : 200,
                "message" : "json ok!"
            }
            app.logger.debug("JSON Ok!")
            return Response(json.dumps(resp_str), status=200, mimetype='application/json')
        except ValidationError as e:
            app.logger.error(str(e))
            message = {
                "status": 500,
                "message": str(e)
            }
            print "Invalid JSON sent."
            return Response(json.dumps(message),status=500, mimetype='application/json')

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    print 'in upload file'
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '' :
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',filename=filename))
    return '''
        <!doctype html>
        <title>Upload new file</title>
        <h1>Upload new file</h1>
        <form action="" method=post enctype=multipart/form-data>
        <p><input type =file name=file><input type=submit value="upload and validate"></form>'''

if __name__ == '__main__':
    app.run()
