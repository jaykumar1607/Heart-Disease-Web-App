from flask import Flask,render_template,url_for,session,redirect,Response
import pandas as pd
import numpy as np
import joblib
from wtforms import FloatField,SubmitField,SelectField
from flask_wtf import FlaskForm
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib
matplotlib.use('Agg')
import io
from plots import Plots

def make_predictions(model,sample_json):

    values = list(sample_json.values())
    np_values = np.array(values)
    predictions = model.predict([np_values])
    if predictions[0]==0:
        return 'NEGATIVE'
    else:
        return 'POSITIVE'


app = Flask(__name__)
app.config['SECRET_KEY']='jaykumar'

class Heart_Form(FlaskForm):

    # Compulsory Field
    thal = SelectField('Thalium Stress Test',choices=[(1,'Fixed Defect'),(2,'Normal'),(3,'Reversible Defect')])
    exang = SelectField('Exercise Induced Angina',choices=[(0,'No'),(1,'Yes')])
    cp = SelectField('Chest Pain Type',choices=[(0,'Asymptomatic'),(1,'Typical Angina'),(2,'Atypical Angina'),(3,'Non-Anginal Pain')])
    ca = SelectField('Number of vessels colored by Fluroscopy',choices=[(0,'0'),(1,'1'),(2,'2'),(3,'3')])
    sex = SelectField('Sex',choices=[(1,'Male'),(0,'Female')])
    oldpeak = FloatField('ST depression induced by exercise relative to rest')
    slope = SelectField('The slope of the peak excercise ST segment',choices=[(0,'Downsloping'),(1,'Flat'),(2,'Upsloping')])

    # Fields for Graphs
    age = FloatField('Age')
    trestbps = FloatField('Resting Systolic Blood Pressure (mm Hg)')
    chol = FloatField('Serum Cholesterol Levels (mg/dl)')
    thalach = FloatField('Maximum Heart Rate Achieved')
    restecg = SelectField('Resting Electrocardiographic Results',choices=[(0,'Hypertrophy'), (1,'Normal'),(2,'ST-T Wave Abnormality')])
    fbs = SelectField('Fasting Blood Sugar Level',choices=[(0,'Less than 120 mg/dl'),(1,'Greater than 120 mg/dl')])

    # Submission Field
    submit = SubmitField('Analyze')


@app.route('/',methods=['GET','POST'])
def home():

    form = Heart_Form()

    if form.validate_on_submit():
        session['thal'] = form.thal.data
        session['exang'] = form.exang.data
        session['cp'] = form.cp.data
        session['ca'] = form.ca.data
        session['sex'] = form.sex.data
        session['oldpeak'] = form.oldpeak.data
        session['slope'] = form.slope.data

        session['age'] = form.age.data
        session['trestbps'] = form.trestbps.data
        session['chol'] = form.chol.data
        session['thalach'] = form.thalach.data
        session['restecg'] = form.restecg.data
        session['fbs'] = form.fbs.data

        return redirect(url_for('prediction'))

    return render_template('prediction.html',form=form)

loaded_model = joblib.load('heart_disease.sav')

@app.route('/prediction')
def prediction():
    content={}
    content['thal'] = session['thal']
    content['exang'] = session['exang']
    content['cp'] = session['cp']
    content['ca'] = session['ca']
    content['sex'] = session['sex']
    content['oldpeak'] = session['oldpeak']
    content['slope'] = session['slope']

    results = make_predictions(loaded_model,content)

    return render_template('result.html',results=results)

# Plots for the analytical report
plots = Plots()

@app.route('/plot_chol.png')
def plot1_png():
    inp=session['chol']
    fig = plots.chol_plot(inp)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route('/plot_bp.png')
def plot2_png():
    inp=session['trestbps']
    fig = plots.bp_plot(inp)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route('/plot_thalach.png')
def plot3_png():
    inp=session['thalach']
    fig = plots.thalach_plot(inp)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


if __name__ == '__main__':
    app.run()
