from types import MethodType
from flask import Flask, render_template, request, redirect, send_from_directory, session
import os
import cv2
from semi_visible_WM import semi_visible_WM

from wtforms.fields.core import FloatField, StringField

app = Flask(__name__)
app.config['SECRET_KEY'] = '12345678'
app.config['UPLOAD_FOLDER'] = 'temp'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
MEDIA_FOLDER = 'temp'

from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField

class semi_visible_pos_form(FlaskForm):
	x = IntegerField(label="x", id='x')
	y = IntegerField(label="y", id='y')
	alpha = FloatField(label="alpha", id='alpha')
	submit = SubmitField(label="Generate")

@app.route('/')
def semi_visible():
	return render_template('semi_visible.html', img="static/out.png")

@app.route('/upload_image')
def upload_image_form():
	return render_template('upload_image.html')

@app.route('/view_image', methods=['POST'])
def view_images():
	if request.method == 'POST':
		if request.files:
			image = request.files['image']
			watermark = request.files['watermark']
			image.save(os.path.join('static', image.filename))
			watermark.save(os.path.join('static', watermark.filename))

			form = semi_visible_pos_form()
			session['image'] = image.filename
			session['watermark'] = watermark.filename
			return render_template('view_image.html', image=image.filename, watermark=watermark.filename,
									form=form)

@app.route('/download_image', methods=['POST'])
def download_image():
	print(request.form)
	req = request.form
	print(req['x'])
	print(session['image'])

	image = cv2.imread(f"static/{session['image']}")
	watermark = cv2.imread(f"static/{session['watermark']}")
	wm_img = semi_visible_WM(image, watermark, pos=[int(req['x']), int(req['y'])])
	cv2.imwrite('static/output1.png', wm_img)
	return render_template("download_image.html", img='static/output1.png')
	

if __name__ == '__main__':
	app.run()