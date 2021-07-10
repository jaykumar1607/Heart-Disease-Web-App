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
import matplotlib.pyplot as plt

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

@app.route('/')
def index():
    return render_template('index.html')

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
df = pd.read_csv('./heart.csv')
colors_red = ["#331313", "#582626", '#9E1717', '#D35151', '#E9B4B4']
colors_dark = ["#1F1F1F", "#313131", '#636363', '#AEAEAE', '#DADADA']

@app.route('/plot.png')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure():
    fig,ax = plt.subplots(figsize=(10,4))

    # Making the KDE plot
    df['chol'].plot.kde(ls='--',color=colors_red[2],ax=ax)

    # Removing the axis
    ax.spines['left'].set_color(None)
    ax.spines['top'].set_color(None)
    ax.spines['right'].set_color(None)

    # Removing labels from y axis
    ax.set_ylabel(None)
    ax.set_yticks([])
    ax.set_xlabel('Serum Cholestrol Level (mg/dl)',fontsize=12)

    # Filling the plot to signify different levels of cholesterol
    line = ax.get_lines()[-1]
    x, y = line.get_data()
    mask1 = x > 200
    mask2 = x>=240
    x1, y1 = x[mask1], y[mask1]
    x2,y2 = x[mask2],y[mask2]
    ax.fill_between(x1, y1, alpha=0.5, facecolor=colors_red[3])
    ax.fill_between(x2, y2, alpha=0.5, facecolor=colors_red[2])

    # y values wrt to x
    vals = pd.DataFrame(y,index=np.round(x))
    inp=session['chol']

    # Making horizontal lines which connect to the text boxes
    ax.hlines(0.0018,xmin=300,xmax=510,ls='-.',color=colors_dark[2],lw=0.8) # High Cholesterol
    ax.hlines(0.005,xmin=225,xmax=500,ls='-.',color=colors_dark[2],lw=0.8)  # Borderline High Cholesterol
    ax.hlines(vals.loc[np.round(inp)],xmin=0,xmax=inp-3,ls='-',color=colors_dark[2],lw=1)  # You are here!

    # Making a point to indicate where the patient stands in the plot
    ax.scatter(inp,vals.loc[np.round(inp)],c=colors_dark[1])

    # Making the text boxes
    fig.text(s='High\nCholesterol',x=0.67,y=0.29,
             fontdict={'color':'white','size':10,'fontweight':'semibold','fontname':'monospace','ha':'center'},
             backgroundcolor=colors_dark[2])
    fig.text(s='Borderline High\nCholesterol',x=0.70,y=0.56,
             fontdict={'color':'white','size':10,'fontweight':'semibold','fontname':'monospace','ha':'center'},
             backgroundcolor=colors_dark[2])
    ax.text(s='You are here!',x=0,y=vals.loc[np.round(inp)],
             fontdict={'color':'white','size':10,'fontweight':'semibold','fontname':'monospace','ha':'center'},
             backgroundcolor=colors_dark[2])

    return fig


if __name__ == '__main__':
    app.run()
