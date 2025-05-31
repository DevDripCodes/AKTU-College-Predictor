from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    round_selected = "Round " + request.form['round'].strip()
    quota = request.form['quota'].strip()
    category = request.form['category'].strip()
    gender = request.form['gender'].strip()
    crl_rank = float(request.form['crl_rank'])

    df = pd.read_csv('cutoff_data.csv')

    for col in ['Round', 'Quota', 'Category', 'Seat Gender']:
        df[col] = df[col].astype(str).str.strip()

    filtered_df = df[
        (df['Round'] == round_selected) &
        (df['Quota'] == quota) &
        (df['Category'] == category) &
        (df['Seat Gender'] == gender)
    ].copy()

    filtered_df['Closing Rank'] = pd.to_numeric(filtered_df['Closing Rank'], errors='coerce')

    result_df = filtered_df[filtered_df['Closing Rank'] >= crl_rank]
    result_df = result_df.sort_values(by='Closing Rank')

    cols_to_drop = ['Sr.No', 'Round', 'Quota', 'Category', 'Seat Gender']
    cols_to_drop += [col for col in result_df.columns if 'Unnamed' in col]
    result_df = result_df.drop(columns=[col for col in cols_to_drop if col in result_df.columns])

    if result_df.empty:
        return render_template('result.html', message="No matching colleges found for your inputs.", tables=[])

    return render_template('result.html', tables=[result_df.to_html(classes='data', index=False, border=0)], titles=result_df.columns.values)

if __name__ == '__main__':
    app.run(debug=True)
