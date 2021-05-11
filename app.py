from types import MethodType
from flask import Flask, render_template, request, redirect, send_from_directory, session
import os
import cv2
from flask.helpers import send_file
from semi_visible_WM import semi_visible_WM
from wtforms.fields.core import FloatField, StringField

import invisible_checksum,invisible_watermarking

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

@app.route('/download/<name>')
def return_files(name):
	return send_file(session[name])

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
	

@app.route('/checksum_watermarking')
def checksum_upload_image_form():
		return render_template('checksum/upload_image.html')

@app.route('/checksum_output', methods=['POST'])
def checksum_download_image():
	if request.method == 'POST':
		if request.files:
			image = request.files['image']
			image.save(os.path.join('static', image.filename))
			w_img,w_key=invisible_checksum.watermark(f'static/{image.filename}')
			session['image'] = w_img
			session['key'] = w_key
			return render_template('checksum/download_image.html', img=w_img, key=w_key)

@app.route('/checksum_watermarking_verify')
def verify_checksum_upload_image_form():
	return render_template('checksum/upload_image_to_extract.html')

@app.route('/invisible_extracted_watermark', methods=['POST'])
def verify_checksum_output():
	if request.method == 'POST':
		if request.files:
			image = request.files['image']
			key = request.files['key']
			image.save(os.path.join('static', image.filename))
			key.save(os.path.join('static', key.filename))
			message = "the image is not authentic"
			if invisible_checksum.check_watermark(f'static/{image.filename}',f'static/{key.filename}'):
				message = "the image is authentic"
			return render_template('checksum/verify_checksum_output.html',message=message)

@app.route('/invisible_watermarking')
def invisible_upload_image_form():
	return render_template('invisible/upload_image.html')

@app.route('/invisible_watermarking_output', methods=['POST'])
def invisible_download_image():
	if request.method == 'POST':
		if request.files:
			image = request.files['image']
			watermark = request.files['watermark']
			image.save(os.path.join('static', image.filename))
			watermark.save(os.path.join('static', watermark.filename))
			w_img,w_key=invisible_watermarking.watermark(f'static/{image.filename}',f'static/{watermark.filename}')
			session['image'] = w_img
			session['key'] = w_key
			return render_template('invisible/download_image.html', img=w_img)

@app.route('/invisible_watermarking_extract')
def extract_invisible_upload_image_form():
	return render_template('invisible/upload_image_to_extract.html')

@app.route('/invisible_extracted_watermark', methods=['POST'])
def extract_invisible_download_image():
	if request.method == 'POST':
		if request.files:
			image = request.files['image']
			key = request.files['key']
			image.save(os.path.join('static', image.filename))
			key.save(os.path.join('static', key.filename))
			extracted_watermark=invisible_watermarking.extract_watermark(f'static/{image.filename}',f'static/{key.filename}')
			session['image'] = extracted_watermark
			return render_template('invisible/download_extracted_watermark.html', img=extracted_watermark)

if __name__ == '__main__':
	app.run()