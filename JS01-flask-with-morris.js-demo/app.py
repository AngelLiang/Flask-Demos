from flask import Flask
from flask import render_template


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/weeks')
@app.route('/template')
def weeks():
    data = [
        {"period": "2011 W27", "licensed": 3407, "sorned": 660},
        {"period": "2011 W26", "licensed": 3351, "sorned": 629},
        {"period": "2011 W25", "licensed": 3269, "sorned": 618},
        {"period": "2011 W24", "licensed": 3246, "sorned": 661},
        {"period": "2011 W23", "licensed": 3257, "sorned": 667},
        {"period": "2011 W22", "licensed": 3248, "sorned": 627},
        {"period": "2011 W21", "licensed": 3171, "sorned": 660},
        {"period": "2011 W20", "licensed": 3171, "sorned": 676},
        {"period": "2011 W19", "licensed": 3201, "sorned": 656},
        {"period": "2011 W18", "licensed": 3215, "sorned": 622},
        {"period": "2011 W17", "licensed": 3148, "sorned": 632},
        {"period": "2011 W16", "licensed": 3155, "sorned": 681},
        {"period": "2011 W15", "licensed": 3190, "sorned": 667},
        {"period": "2011 W14", "licensed": 3226, "sorned": 620},
        {"period": "2011 W13", "licensed": 3245, "sorned": None},
        {"period": "2011 W12", "licensed": 3289, "sorned": None},
        {"period": "2011 W11", "licensed": 3263, "sorned": None},
        {"period": "2011 W10", "licensed": 3189, "sorned": None},
        {"period": "2011 W09", "licensed": 3079, "sorned": None},
        {"period": "2011 W08", "licensed": 3085, "sorned": None},
        {"period": "2011 W07", "licensed": 3055, "sorned": None},
        {"period": "2011 W06", "licensed": 3063, "sorned": None},
        {"period": "2011 W05", "licensed": 2943, "sorned": None},
        {"period": "2011 W04", "licensed": 2806, "sorned": None},
        {"period": "2011 W03", "licensed": 2674, "sorned": None},
        {"period": "2011 W02", "licensed": 1702, "sorned": None},
        {"period": "2011 W01", "licensed": 1732, "sorned": None}
    ]
    return render_template('data_from_template.html', data=data)


@app.route('/years')
def years():
    data = [
        {"period": "2012", "licensed": 3407, "sorned": 660},
        {"period": "2011", "licensed": 3351, "sorned": 629},
        {"period": "2010", "licensed": 3269, "sorned": 618},
        {"period": "2009", "licensed": 3246, "sorned": 661},
        {"period": "2008", "licensed": 3257, "sorned": 667},
        {"period": "2007", "licensed": 3248, "sorned": 627},
        {"period": "2006", "licensed": 3171, "sorned": 660},
        {"period": "2005", "licensed": 3171, "sorned": 676},
        {"period": "2004", "licensed": 3201, "sorned": 656},
        {"period": "2003", "licensed": 3215, "sorned": 622}
    ]
    return render_template('data_from_template.html', data=data)


@app.route('/timestamps')
def timestamps():
    data = [
        {"period": 1349046000000, "licensed": 3407, "sorned": 660},
        {"period": 1313103600000, "licensed": 3351, "sorned": 629},
        {"period": 1299110400000, "licensed": 3269, "sorned": 618},
        {"period": 1281222000000, "licensed": 3246, "sorned": 661},
        {"period": 1273446000000, "licensed": 3257, "sorned": 667},
        {"period": 1268524800000, "licensed": 3248, "sorned": 627},
        {"period": 1263081600000, "licensed": 3171, "sorned": 660},
        {"period": 1260403200000, "licensed": 3171, "sorned": 676},
        {"period": 1254870000000, "licensed": 3201, "sorned": 656},
        {"period": 1253833200000, "licensed": 3215, "sorned": 622}
    ]
    return render_template('data_from_template.html', data=data)


@app.route('/months')
def months():
    data = [
        {"period": "2012-10", "licensed": 3407, "sorned": 660},
        {"period": "2011-08", "licensed": 3351, "sorned": 629},
        {"period": "2011-03", "licensed": 3269, "sorned": 618},
        {"period": "2010-08", "licensed": 3246, "sorned": 661},
        {"period": "2010-05", "licensed": 3257, "sorned": 667},
        {"period": "2010-03", "licensed": 3248, "sorned": 627},
        {"period": "2010-01", "licensed": 3171, "sorned": 660},
        {"period": "2009-12", "licensed": 3171, "sorned": 676},
        {"period": "2009-10", "licensed": 3201, "sorned": 656},
        {"period": "2009-09", "licensed": 3215, "sorned": 622}
    ]
    return render_template('data_from_template.html', data=data)


@app.route('/days')
def days():
    data = [
        {"period": "2012-10-01", "licensed": 3407, "sorned": 660},
        {"period": "2012-09-30", "licensed": 3351, "sorned": 629},
        {"period": "2012-09-29", "licensed": 3269, "sorned": 618},
        {"period": "2012-09-20", "licensed": 3246, "sorned": 661},
        {"period": "2012-09-19", "licensed": 3257, "sorned": 667},
        {"period": "2012-09-18", "licensed": 3248, "sorned": 627},
        {"period": "2012-09-17", "licensed": 3171, "sorned": 660},
        {"period": "2012-09-16", "licensed": 3171, "sorned": 676},
        {"period": "2012-09-15", "licensed": 3201, "sorned": 656},
        {"period": "2012-09-10", "licensed": 3215, "sorned": 622}
    ]
    return render_template('data_from_template.html', data=data)


@app.route('/quarters')
def quarters():
    data = [
        {"period": "2011 Q3", "licensed": 3407, "sorned": 660},
        {"period": "2011 Q2", "licensed": 3351, "sorned": 629},
        {"period": "2011 Q1", "licensed": 3269, "sorned": 618},
        {"period": "2010 Q4", "licensed": 3246, "sorned": 661},
        {"period": "2010 Q3", "licensed": 3257, "sorned": 667},
        {"period": "2010 Q2", "licensed": 3248, "sorned": 627},
        {"period": "2010 Q1", "licensed": 3171, "sorned": 660},
        {"period": "2009 Q4", "licensed": 3171, "sorned": 676},
        {"period": "2009 Q3", "licensed": 3201, "sorned": 656},
        {"period": "2009 Q2", "licensed": 3215, "sorned": 622},
        {"period": "2009 Q1", "licensed": 3148, "sorned": 632},
        {"period": "2008 Q4", "licensed": 3155, "sorned": 681},
        {"period": "2008 Q3", "licensed": 3190, "sorned": 667},
        {"period": "2007 Q4", "licensed": 3226, "sorned": 620},
        {"period": "2006 Q4", "licensed": 3245, "sorned": None},
        {"period": "2005 Q4", "licensed": 3289, "sorned": None},
        {"period": "2004 Q4", "licensed": 3263, "sorned": None},
        {"period": "2003 Q4", "licensed": 3189, "sorned": None},
        {"period": "2002 Q4", "licensed": 3079, "sorned": None},
        {"period": "2001 Q4", "licensed": 3085, "sorned": None},
        {"period": "2000 Q4", "licensed": 3055, "sorned": None},
        {"period": "1999 Q4", "licensed": 3063, "sorned": None},
        {"period": "1998 Q4", "licensed": 2943, "sorned": None},
        {"period": "1997 Q4", "licensed": 2806, "sorned": None},
        {"period": "1996 Q4", "licensed": 2674, "sorned": None},
        {"period": "1995 Q4", "licensed": 1702, "sorned": None},
        {"period": "1994 Q4", "licensed": 1732, "sorned": None}
    ]
    return render_template('data_from_template.html', data=data)


if __name__ == "__main__":
    app.run(debug=True)
