from flask import Flask, request, url_for, render_template, session, send_file
import pandas as pd
from utils import serp_search, ddg_search, extract_info
import re
import io

app = Flask(__name__, template_folder='templates')
app.secret_key = 'your-secret-key-here'


@app.route('/download_results')
def download_results():
    if 'df' not in session:
        return "No results to download"
        
    try:
        # Create DataFrame from session data
        results_df = pd.read_json(session.get('results', '[]'))
        
        # Convert to CSV
        output = io.StringIO()
        results_df.to_csv(output, index=False)
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='search_results.csv'
        )
    except Exception as e:
        return str(e)


@app.route('/', methods=['GET', 'POST'])
def index():
    file_supported = None
    original_table = None
    results_table = None
    error_message = None
    
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file:
                try:
                    if file.content_type == 'text/csv' or file.filename.endswith('.csv'):
                        df = pd.read_csv(file)
                    elif file.content_type == 'application/vnd.ms-excel' or file.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or file.filename.endswith(('.xls', '.xlsx')):
                        df = pd.read_excel(file)
                    else:
                        file_supported = 'Failure'
                        return render_template('index.html', file_supported=file_supported)
                    
                    # Clean DataFrame - replace newlines
                    df = df.replace(r'\n', ' ', regex=True)
                    
                    session['df'] = df.to_json()
                    original_table = df.to_html(classes='table table-striped', index=False, escape=False)
                    file_supported = 'Success'
                    
                except Exception as e:
                    file_supported = 'Failure'
                    error_message = str(e)
        
        elif all(key in request.form for key in ['api_key_search', 'api_key_llm', 'prompt_global']):
            if 'df' not in session:
                error_message = "Please upload a file first"
                return render_template('index.html', error_message=error_message)
            
            try:
                df = pd.read_json(session['df'])
                api_choice = request.form.get('dropdown')
                api_key_search = request.form.get('api_key_search')
                api_key_llm = request.form.get('api_key_llm')
                prompt_template = request.form.get('prompt_global').replace('\n', ' ')
                
                column_vars = re.findall(r'\{(\w+)\}', prompt_template)
                missing_cols = [col for col in column_vars if col not in df.columns]
                if missing_cols:
                    error_message = f"Columns not found in file: {', '.join(missing_cols)}"
                    return render_template('index.html', error_message=error_message, table_html=df.to_html(classes='table table-striped', index=False))
                
                results = []
                
                for index, row in df.iterrows():
                    try:
                        prompt = prompt_template.format(**row.to_dict())
                        row_search = serp_search(prompt, api_key_search) if api_choice == 'serp_api' else ddg_search(prompt)
                        
                        if row_search.get("status") == "error":
                            error_message = row_search.get("message")
                            return render_template('index.html', error_message=error_message)

                        row_info = extract_info(row_search, prompt, api_key_llm)
                        if row_info.get("status") == "error":
                            error_message = row_info.get("message")
                            return render_template('index.html', error_message=error_message)
                        
                        # Clean extracted data
                        extracted_data = [str(item).replace('\n', ' ') for item in row_info.get("extracted_data", [])]
                        summary = row_info.get("summary", "").replace('\n', ' ')
                        
                        results.append({
                            "Original Entry": row['company'],
                            "Extracted Data": extracted_data,
                            "Summary": summary
                        })
                        
                    except KeyError as e:
                        error_message = f"Error formatting prompt: {str(e)}"
                        return render_template('index.html', error_message=error_message)
                
                results_df = pd.DataFrame(results)
                results_table = results_df.to_html(classes='table table-striped', index=False, escape=False)
                original_table = pd.read_json(session['df']).to_html(classes='table table-striped', index=False, escape=False)
                file_supported = 'Success'
                if 'results_df' in locals():
                    session['results'] = results_df.to_json()
    
                
            except Exception as e:
                error_message = str(e)
                if results:
                    results_df = pd.DataFrame(results)
    
    return render_template('index.html', original_table=original_table, results_table=results_table, file_supported=file_supported, error_message=error_message, has_results='results_df' in locals())

""" 
    MAIN
"""
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5555, debug=True)