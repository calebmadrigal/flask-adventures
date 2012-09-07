from flask import Flask
from flask import request, redirect, url_for
import datetime
import sys

app = Flask(__name__)

# This lets me change what I redirect to from my "homepage" (caleb.pythonanywhere.com).
@app.route('/')
def index():
    return redirect(url_for('annuitycalc'))

@app.route('/annuitycalc', methods=['GET', 'POST'])
def annuitycalc():
    if request.method == "GET":
        return generate_form()
    else:
        initial_amount = float(value_or_zero(request.form,'initial_amount'))
        addition_per_year = float(value_or_zero(request.form,'addition_per_year'))
        interest = float(value_or_zero(request.form,'interest'))
        years = int(value_or_zero(request.form,'years'))
        start_year = datetime.datetime.now().year

        year_list = generate_year_list(start_year, years)
        annuity_by_year = calculate_annuity(years, interest, addition_per_year, initial_amount)

        return generate_graph(year_list, annuity_by_year, "Annuity")

def value_or_zero(request_form, field_name):
    retval = 0
    if request_form.has_key(field_name) and request_form[field_name] != '':
        retval = request_form[field_name]
    return retval

def calculate_annuity(years, interest=0, addition_per_year=0, starting_amount=0):
    return reduce(lambda total, addition: total + [(total[-1] + addition) * (1 + interest)], [addition_per_year] * years, [starting_amount])[1:]

def generate_year_list(start_year, number_years):
    return range(start_year, start_year+number_years+1)

def generate_form():
    return """
            <form action="/annuitycalc" method="POST">
                <table>
                <tr><td>Initial Amount</td><td><input type="text" name="initial_amount" /></td></tr>
                <tr><td>Addition Per Year</td><td><input type="text" name="addition_per_year" /></td></tr>
                <tr><td>Interest</td><td><input type="text" name="interest" /></td></tr>
                <tr><td>Years to Project</td><td><input type="text" name="years" /></td></tr>
                </table>
                <input type="submit" />
            </form>
        """

def generate_graph(x_axis, y_axis, title=''):
    return """
    <html><head>
        <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
        <script type="text/javascript">
            $(function () {
                var chart;
                $(document).ready(function() {
                    chart = new Highcharts.Chart({
                        chart: {
                            renderTo: 'container',
                            type: 'line',
                            marginRight: 130,
                            marginBottom: 100
                        },
                        title: {
                            text: '%(title)s',
                            x: -20 //center
                        },
                        subtitle: {
                            text: '',
                            x: -20
                        },
                        xAxis: {
                            categories: %(x_axis)s,
                            labels: {
                                rotation: -45,
                                align: 'right'
                            }
                        },
                        yAxis: {
                            title: {
                                text: 'Dollars'
                            },
                            plotLines: [{
                                value: 0,
                                width: 1,
                                color: '#808080'
                            }]
                        },
                        tooltip: {
                            formatter: function() {
                                    return '<b>'+ this.series.name +'</b><br/>'+
                                    this.x +': '+ this.y;
                            }
                        },
                        legend: {
                            layout: 'vertical',
                            align: 'right',
                            verticalAlign: 'top',
                            x: -10,
                            y: 100,
                            borderWidth: 0
                        },
                        series: [{
                            name: 'Net Worth',
                            data: %(y_axis)s
                        }]
                    });
                });

            });
        </script>
    </head><body>
    <script src="http://test.calebmadrigal.com/jshost/highcharts/highcharts.js"></script>
    <script src="http://test.calebmadrigal.com/jshost/highcharts/modules/exporting.js"></script>

    <div id="container" style="min-width: 400px; height: 400px; margin: 0 auto"></div>
    </body></html>
    """ % {'x_axis': str(x_axis), 'y_axis': str(y_axis), 'title': title }
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: python annuity_calculator.py <port number>"
        sys.exit(1)
        
    p = int(sys.argv[1])
    app.debug = True
    app.run(host='0.0.0.0', port=p)
