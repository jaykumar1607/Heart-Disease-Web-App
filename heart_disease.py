from flask import Flask,render_template,url_for,session,redirect,Response
import pandas as pd
import numpy as np
import joblib
from wtforms import FloatField,SubmitField,SelectField,StringField
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

def report_cat(feature_name,feature_value):
    cat_feat={
        'cp':{
            0:'You have Asymptomatic Pain which puts you at a lower chance of causing a heart disease, at 27% risk',
            1:'You have Typical Angina which puts you at a higher chance of causing a heart disease, at 82% risk',
            2:'You have Atypical Angina which puts you at a higher chance of causing a heart disease, at 78% risk',
            3:'You have Non-Anginal Pain which puts you at a moderately higher chance of causing a heart disease, at 69% risk'
        },
        'fbs':{
            0:'You are not Diabetic which is healthier for your heart',
            1:'You are Diabetic, so we advice you to keep a check on it because high Diabetic levels can lead to a heart disease'
        },
        'exang':{
            0:'You have no Exercise Induced Angina and are at a higher risk of having a heart disease, at 69% risk',
            1:'You have Exercise Induced Angina and are at a lower risk of having a heart disease, at 23% risk'
        },
        'slope':{
            0:'You have a Downsloping slope in the peak exercise ST segment which puts you at a moderate risk of having a heart disease, at 43% risk',
            1:'You have a Flat slope in the peak exercise ST segment which puts you at a lower risk of having a heart disease, at 35% risk',
            2:'You have a Upsloping slope in the peak exercise ST segment which puts you at a higher risk of having a heart disease, at 75% risk'
        },
        'thal':{
            1:'You have a "Fixed Defect" Thalium Stress Test result which puts you at a lower risk of having a heart disease, at 33% risk',
            2:'You have a "Normal" Thalium Stress Test result which puts you at a higher risk of having a heart disease, at 77% risk',
            3:'You have a "Reversible Defect" Thalium Stress Test result which puts you at a lower risk of having a heart disease, at 23% risk'
        },
        'ca':{
            0:'You have 0 colored vessels after Fluoroscopy which puts you at higher risk of having a heart disease, at 74% risk',
            1:'You have 1 colored vessels after Fluoroscopy which puts you at lower risk of having a heart disease, at 32% risk',
            2:'You have 2 colored vessels after Fluoroscopy which puts you at lower risk of having a heart disease, at 18% risk',
            3:'You have 3 colored vessels after Fluoroscopy which puts you at lower risk of having a heart disease, at 15% risk'
        }
    }
    return cat_feat[feature_name][feature_value]

def report_cont(feat):
    if feat=='chol':
        if float(session['chol'])>200 and float(session['chol'])<=240:
            return 'You have borderline high Cholesterol levels which puts you at a moderately high risk of having a heart disease'
        elif float(session['chol']>240):
            return 'You have high Cholesterol levels which puts you at a higher risk of having a heart disease'
        else:
            return 'You have normal Cholesterol levels which puts you at a lower risk of having a heart disease'
    elif feat=='trestbps':
        if float(session['trestbps'])>140:
            return 'You have high Resting Blood Pressure which suggests that you have Hypertension'
        else:
            return 'You have normal Resting Blood Pressure which puts you at a low risk of having a heart disease'
    elif feat=='thalach':
        if float(session['thalach']>180):
            return 'You have a very high Maximum Heart Rate levels (during exercise) which could be dangerous for your heart'
        else:
            return 'Your Maximum Heart Rate levels (during exercise) lie within a safe and normal range'


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
    name = StringField('Patient\'s Name')
    age = FloatField('Age')
    trestbps = FloatField('Resting Systolic Blood Pressure (mm Hg)')
    chol = FloatField('Serum Cholesterol Levels (mg/dl)')
    thalach = FloatField('Maximum Heart Rate Achieved')
    restecg = SelectField('Resting Electrocardiographic Results',choices=[(0,'Hypertrophy'), (1,'Normal'),(2,'ST-T Wave Abnormality')])
    fbs = SelectField('Fasting Blood Sugar Level',choices=[(0,'Less than 120 mg/dl'),(1,'Greater than 120 mg/dl')])

    # Submission Field
    submit = SubmitField('Analyze')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/predict',methods=['GET','POST'])
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

        session['name']=form.name.data
        session['age'] = form.age.data
        session['trestbps'] = form.trestbps.data
        session['chol'] = form.chol.data
        session['thalach'] = form.thalach.data
        session['restecg'] = form.restecg.data
        session['fbs'] = form.fbs.data

        return redirect(url_for('prediction'))

    return render_template('prediction.html',form=form)

loaded_model = joblib.load('heart_disease.sav')

@app.route('/result')
def prediction():
    content={}
    reports={}
    content['thal'] = session['thal']
    content['exang'] = session['exang']
    content['cp'] = session['cp']
    content['ca'] = session['ca']
    content['sex'] = session['sex']
    content['oldpeak'] = session['oldpeak']
    content['slope'] = session['slope']

    labels1=['cp','fbs','exang','slope','thal','ca']
    labels2=['chol','trestbps','thalach']
    for i in labels1:
        reports[i]=report_cat(i,int(session[i]))
    for i in labels2:
        reports[i]=report_cont(i)

    results = make_predictions(loaded_model,content)

    return render_template('result.html',results=results, reports = reports)

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
