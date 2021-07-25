import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

index=['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach',
       'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target']
df = pd.read_csv('heart.csv',names=index,header=0)

colors_red = ["#331313", "#582626", '#9E1717', '#D35151', '#E9B4B4']
colors_dark = ["#1F1F1F", "#313131", '#636363', '#AEAEAE', '#DADADA']
colors_purple = ["#554f8a", "#8a94cd", "#ada3e0", "#ab92c3", "#ebebf3"]
class Plots():
    def chol_plot(self,inp):
        fig,ax = plt.subplots(figsize=(10,4),facecolor="#ebebeb")
        ax.set_facecolor("#ebebeb")
        # Making the KDE plot
        df['chol'].plot.kde(ls='--',color=colors_purple[0],ax=ax)

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
        ax.fill_between(x1, y1, alpha=0.5, facecolor=colors_purple[3])
        ax.fill_between(x2, y2, alpha=0.5, facecolor=colors_purple[1])

        # y values wrt to x
        vals = pd.DataFrame(y,index=np.round(x))

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

    def bp_plot(self,inp):

        fig,ax = plt.subplots(figsize=(10,4))

        df['trestbps'].plot.kde(ls='--',color=colors_purple[0],ax=ax)

        ax.spines['left'].set_color(None)
        ax.spines['top'].set_color(None)
        ax.spines['right'].set_color(None)

        ax.set_ylabel(None)
        ax.set_yticks([])
        ax.set_xlabel('Resting Blood Pressure (mm Hg)',fontsize=12)

        line = ax.get_lines()[-1]
        x,y = line.get_data()
        mask = x>140
        x1,y1 = x[mask],y[mask]
        ax.fill_between(x1,y1,alpha=0.7,facecolor = colors_purple[1])

        # y values wrt to x
        vals = pd.DataFrame(y,index=np.round(x))

        # Making a point to indicate where the patient stands in the plot
        ax.scatter(inp,vals.loc[np.round(inp)].iloc[0][0],c=colors_dark[1])

        fig.text(s='Patients with\n Hypertension',x=0.70,y=0.38,
                 fontdict={'color':'white','size':10,'fontweight':'semibold','fontname':'monospace','ha':'center'},
                 backgroundcolor=colors_dark[2])
        ax.text(s='You are here!',x=50,y=vals.loc[np.round(inp)].iloc[0][0],
                 fontdict={'color':'white','size':10,'fontweight':'semibold','fontname':'monospace','ha':'center'},
                 backgroundcolor=colors_dark[2])
        ax.hlines(0.0085,xmin=145,xmax=200,ls='-.',color=colors_dark[2],lw=0.8)
        ax.hlines(vals.loc[np.round(inp)].iloc[0][0],xmin=50,xmax=inp-2,ls='-',color=colors_dark[2],lw=1)  # You are here!

        return fig

    def thalach_plot(self,inp):
        fig,ax = plt.subplots(figsize=(10,4))

        df['thalach'].plot.kde(ls='--',color=colors_purple[0],ax=ax)

        ax.spines['left'].set_color(None)
        ax.spines['top'].set_color(None)
        ax.spines['right'].set_color(None)

        ax.set_ylabel(None)
        ax.set_yticks([])
        ax.set_xlabel('Max. Heart Rate achieved during exercise (BPM)',fontsize=12)

        line = ax.get_lines()[-1]
        x,y = line.get_data()
        mask = x>180
        x1,y1 = x[mask],y[mask]
        ax.fill_between(x1,y1,alpha=0.7,facecolor = colors_purple[1])

        # y values wrt to x
        vals = pd.DataFrame(y,index=np.round(x))

        # Making a point to indicate where the patient stands in the plot
        ax.scatter(inp,vals.loc[np.round(inp)].iloc[0][0],c=colors_dark[1])

        fig.text(s='Dangerous Heart\n Rate level',x=0.800,y=0.25,
                 fontdict={'color':'white','size':10,'fontweight':'semibold','fontname':'monospace','ha':'center'},
                 backgroundcolor=colors_dark[2])
        ax.text(s='You are here!',x=50,y=vals.loc[np.round(inp)].iloc[0][0],
                fontdict={'color':'white','size':10,'fontweight':'semibold','fontname':'monospace','ha':'center'},
                backgroundcolor=colors_dark[2])
        ax.hlines(0.003,xmin=185,xmax=240,ls='-.',color=colors_dark[2],lw=0.8)
        ax.hlines(vals.loc[np.round(inp)].iloc[0][0],xmin=50,xmax=inp-2,ls='-',color=colors_dark[2],lw=1)  # You are here!

        return fig
