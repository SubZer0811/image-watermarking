from types import MethodType
from flask import Flask, render_template, request, redirect, send_from_directory, session
import os
import cv2
from flask.helpers import send_file
from semi_visible_WM import semi_visible_WM
from wtforms.fields.core import FloatField, StringField

import invisible_checksum, invisible_watermarking, wavelet_watermarking, svd_watermarking

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

@app.route('/download_file/<name>')
def file_respond(name):
	return send_file(f'static/{name}', as_attachment=True)

@app.route('/download/<name>')
def return_files(name):
	return send_file(session[name], as_attachment=True)

@app.route('/')
def home():
	return render_template('index.html')

@app.route('/sv_upload_image')
def upload_image_form():
	return render_template('semi-visible/upload_image.html')

@app.route('/sv_view_image', methods=['POST'])
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
			return render_template('semi-visible/view_image.html', image=f'static/{image.filename}', watermark=f'static/{watermark.filename}',
									form=form)

@app.route('/sv_download_image', methods=['POST'])
def download_image():
	print(request.form)
	req = request.form
	print(req['x'])
	print(session['image'])

	image = cv2.imread(f"static/{session['image']}")
	watermark = cv2.imread(f"static/{session['watermark']}")
	wm_img = semi_visible_WM(image, watermark, pos=[int(req['x']), int(req['y'])], alpha=float(req['alpha']))
	cv2.imwrite('static/output.png', wm_img)
	return render_template("semi-visible/download_image.html", img='output.png')
	

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

@app.route('/checksum_verificatiom', methods=['POST'])
def verify_checksum_output():
	if request.method == 'POST':
		if request.files:
			image = request.files['image']
			key = request.files['key']
			image.save(os.path.join('static', image.filename))
			key.save(os.path.join('static', key.filename))
			output = "static/assets/fake.png"
			if invisible_checksum.check_watermark(f'static/{image.filename}',f'static/{key.filename}'):
				output = "static/assets/original.png"
			return render_template('checksum/verify_checksum_output.html',output=output)

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

@app.route('/wavelet_watermarking')
def wavelet_upload_image_form():
	return render_template('wavelet/upload_image.html')

@app.route('/wavelet_watermarking_output', methods=['POST'])
def wavelet_download_image():
	if request.method == 'POST':
		if request.files:
			image = request.files['image']
			watermark = request.files['watermark']
			image.save(os.path.join('static', image.filename))
			watermark.save(os.path.join('static', watermark.filename))
			w_img=wavelet_watermarking.watermark(f'static/{image.filename}',f'static/{watermark.filename}')
			session['image'] = w_img
			return render_template('wavelet/download_image.html', img=w_img)

@app.route('/wavelet_watermarking_extract')
def extract_wavelet_upload_image_form():
	return render_template('wavelet/upload_image_to_extract.html')

@app.route('/wavelet_extracted_watermark', methods=['POST'])
def extract_wavelet_download_image():
	if request.method == 'POST':
		if request.files:
			image = request.files['original_image']
			watermarked_image = request.files['watermarked_image']
			image.save(os.path.join('static', image.filename))
			watermarked_image.save(os.path.join('static', watermarked_image.filename))
			extracted_watermark=wavelet_watermarking.extract_watermark(f'static/{image.filename}',f'static/{watermarked_image.filename}')
			session['image'] = extracted_watermark
			return render_template('wavelet/download_extracted_watermark.html', img=extracted_watermark)

@app.route('/svd_watermarking')
def svd_upload_image_form():
	return render_template('svd/upload_image.html')

@app.route('/svd_watermarking_output', methods=['POST'])
def svd_download_image():
	if request.method == 'POST':
		if request.files:
			image = request.files['image']
			watermark = request.files['watermark']
			image.save(os.path.join('static', image.filename))
			watermark.save(os.path.join('static', watermark.filename))
			w_img=svd_watermarking.watermark(f'static/{image.filename}',f'static/{watermark.filename}')
			session['image'] = w_img
			return render_template('svd/download_image.html', img=w_img)

@app.route('/svd_watermarking_extract')
def extract_svd_upload_image_form():
	return render_template('svd/upload_image_to_extract.html')

@app.route('/svd_extracted_watermark', methods=['POST'])
def extract_svd_download_image():
	if request.method == 'POST':
		if request.files:
			image = request.files['original_image']
			watermark = request.files['original_watermark']
			watermarked_image = request.files['watermarked_image']
			image.save(os.path.join('static', image.filename))
			watermark.save(os.path.join('static', watermark.filename))
			watermarked_image.save(os.path.join('static', watermarked_image.filename))
			extracted_watermark=svd_watermarking.extract_watermark(f'static/{image.filename}',f'static/{watermark.filename}',f'static/{watermarked_image.filename}')
			session['image'] = extracted_watermark
			return render_template('svd/download_extracted_watermark.html', img=extracted_watermark)

if __name__ == '__main__':
	app.run()